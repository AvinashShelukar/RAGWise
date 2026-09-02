import faiss
import numpy as np
import pickle
from pathlib import Path


VECTORSTORE_DIR = Path("vectorstore")

INDEX_PATH = VECTORSTORE_DIR / "index.faiss"
METADATA_PATH = VECTORSTORE_DIR / "metadata.pkl"


def create_vector_store(chunks, embeddings):

    VECTORSTORE_DIR.mkdir(
        exist_ok=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    dimension = embeddings.shape[1]

    print(
        f"Creating FAISS index with dimension {dimension}"
    )

    # Inner Product similarity
    # Works well with normalized embeddings
    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    with open(
        METADATA_PATH,
        "wb"
    ) as file:

        pickle.dump(
            chunks,
            file
        )

    print(
        f"Stored {index.ntotal} vectors."
    )


def load_vector_store():

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            "FAISS index not found. "
            "Run ingestion first."
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Metadata file not found. "
            "Run ingestion first."
        )

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    with open(
        METADATA_PATH,
        "rb"
    ) as file:

        metadata = pickle.load(file)

    return index, metadata