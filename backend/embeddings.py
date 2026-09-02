from sentence_transformers import SentenceTransformer


class EmbeddingModel:

    def __init__(self):

        print("Loading embedding model...")

        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

        print("Embedding model loaded.")

    def encode(self, texts):

        return self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )