
import numpy as np

from backend.embeddings import EmbeddingModel
from backend.vector_store import load_vector_store


class Retriever:

    def __init__(self):
        print("Loading vector database...")

        self.index, self.metadata = load_vector_store()
        self.embedding_model = EmbeddingModel()

        self.documents = sorted({
            item["source"] for item in self.metadata
        })

        print(f"Loaded {self.index.ntotal} vectors.")
        print("Available documents:", self.documents)

    def search(self, query, top_k=5, source=None):

        if not query or not query.strip():
            return []

        query_embedding = self.embedding_model.encode([query])
        query_embedding = np.asarray(
            query_embedding, dtype="float32"
        )

        candidate_k = min(
            max(top_k * 4, 20),
            self.index.ntotal
        )

        scores, indices = self.index.search(
            query_embedding, candidate_k
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            item = self.metadata[idx]

            # Optionally restrict results to one PDF.
            if source and item["source"] != source:
                continue

            score = float(score)

            if score < 0.50:
                continue

            result = item.copy()
            result["score"] = score
            results.append(result)

            if len(results) >= top_k:
                break

        return results
