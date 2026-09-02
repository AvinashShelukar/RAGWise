from pdf_processor import extract_text_from_pdf
from chunker import chunk_documents


PDF_PATH = "data/pdfs/basepaper.pdf"


pages = extract_text_from_pdf(PDF_PATH)

print(f"Pages: {len(pages)}")


chunks = chunk_documents(pages)

print(f"Chunks: {len(chunks)}")


for i, chunk in enumerate(chunks[:5]):

    print("\n" + "=" * 60)

    print(f"Chunk: {i + 1}")
    print(f"Source: {chunk['source']}")
    print(f"Page: {chunk['page']}")

    print("\nText:")
    print(chunk["text"][:500])