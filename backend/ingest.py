from pathlib import Path

from backend.pdf_processor import extract_text_from_pdf
from backend.chunker import chunk_documents
from backend.embeddings import EmbeddingModel
from backend.vector_store import create_vector_store


PDF_FOLDER = Path("data/pdfs")


def ingest_pdfs():

    all_chunks = []

    pdf_files = list(
        PDF_FOLDER.glob("*.pdf")
    )

    if not pdf_files:

        print(
            "No PDF files found in data/pdfs/"
        )

        return

    print(
        f"Found {len(pdf_files)} PDF file(s)."
    )

    for pdf_path in pdf_files:

        print("\n" + "=" * 60)

        print(
            f"Processing: {pdf_path.name}"
        )

        pages = extract_text_from_pdf(
            str(pdf_path)
        )

        print(
            f"Extracted pages: {len(pages)}"
        )

        chunks = chunk_documents(
            pages
        )

        print(
            f"Created chunks: {len(chunks)}"
        )

        all_chunks.extend(
            chunks
        )

    if not all_chunks:

        print(
            "No text chunks were generated."
        )

        return

    print("\n" + "=" * 60)

    print(
        f"Total chunks: {len(all_chunks)}"
    )

    print(
        "Generating embeddings..."
    )

    embedding_model = EmbeddingModel()

    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    embeddings = embedding_model.encode(
        texts
    )

    print(
        f"Embedding shape: {embeddings.shape}"
    )

    create_vector_store(
        all_chunks,
        embeddings
    )

    print("\nIngestion completed successfully.")


if __name__ == "__main__":

    ingest_pdfs()