import os

import numpy as np
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


class EmbeddingModel:
    def __init__(self):
        print("Initializing Hugging Face embedding model...")

        token = os.getenv("HF_TOKEN")

        if not token:
            raise RuntimeError(
                "HF_TOKEN is not set. Add it to your .env file."
            )

        self.client = InferenceClient(token=token)
        self.model = "BAAI/bge-small-en-v1.5"

        print("Hugging Face embedding model ready.")

    def encode(self, texts):
        if not texts:
            return np.empty((0, 384), dtype="float32")

        all_embeddings = []

        # Process in small batches.
        for start in range(0, len(texts), 32):
            batch = texts[start:start + 32]

            result = self.client.feature_extraction(
                batch,
                model=self.model
            )

            batch_embeddings = np.asarray(
                result,
                dtype="float32"
            )

            # Handle a single-vector response.
            if batch_embeddings.ndim == 1:
                batch_embeddings = batch_embeddings.reshape(1, -1)

            all_embeddings.append(batch_embeddings)

        embeddings = np.vstack(all_embeddings)

        # Normalize for FAISS Inner Product / cosine similarity.
        norms = np.linalg.norm(
            embeddings,
            axis=1,
            keepdims=True
        )

        embeddings = embeddings / np.maximum(norms, 1e-12)

        return embeddings