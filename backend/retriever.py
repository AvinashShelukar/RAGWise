
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

        # Validate query
        if not query or not query.strip():
            return []

        if not 1 <= top_k <= 20:
            raise ValueError(
                "top_k must be between 1 and 20."
            )

        # Validate selected document
        if source and source not in self.documents:
            raise ValueError(
                f"Unknown PDF: {source}. "
                f"Available PDFs: {', '.join(self.documents)}"
            )

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        # If a PDF is selected, search the complete index.
        # Otherwise, use a limited candidate search.
        if source:
            candidate_k = self.index.ntotal
        else:
            candidate_k = min(
                max(top_k * 4, 20),
                self.index.ntotal
            )

        # FAISS similarity search
        scores, indices = self.index.search(
            query_embedding,
            candidate_k
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            item = self.metadata[idx]

            # Filter results by selected PDF
            if source and item["source"] != source:
                continue

            score = float(score)

            # Existing similarity threshold
            if score < 0.50:
                continue

            # Preserve original metadata and citation details
            result = item.copy()
            result["score"] = score

            results.append(result)

            if len(results) >= top_k:
                break

        return results
