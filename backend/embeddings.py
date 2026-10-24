from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingModel:

    def __init__(self):

        print(
            "Loading local BGE embedding model..."
        )

        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

        print(
            "Local embedding model ready."
        )

    def encode(self, texts):

        if not texts:
            return np.empty(
                (0, 384),
                dtype="float32"
            )

        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return np.asarray(
            embeddings,
            dtype="float32"
        )
