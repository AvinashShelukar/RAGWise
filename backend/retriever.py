import numpy as np

from backend.embeddings import EmbeddingModel
from backend.vector_store import load_vector_store


class Retriever:

    def __init__(self):

        print("Loading vector database...")

        self.index, self.metadata = \
            load_vector_store()

        self.embedding_model = \
            EmbeddingModel()

        print(
            f"Loaded {self.index.ntotal} vectors."
        )

    def search(
        self,
        query,
        top_k=5
    ):

        query_embedding = \
            self.embedding_model.encode(
                [query]
            )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        scores, indices = \
            self.index.search(
                query_embedding,
                top_k
            )

        results = []

        for score, idx in zip(
            scores[0],
            indices[0]
        ):

            if idx == -1:
                continue

            result = self.metadata[idx].copy()

            result["score"] = float(score)

            results.append(result)

        return results