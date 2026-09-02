import pymupdf
from pathlib import Path


def extract_text_from_pdf(pdf_path):

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document):

        text = page.get_text()

        if text.strip():

            pages.append({
                "text": text,
                "page": page_number + 1,
                "source": Path(pdf_path).name
            })

    document.close()

    return pages


if __name__ == "__main__":

    pdf_path = "data/pdfs/basepaper.pdf"

    pages = extract_text_from_pdf(pdf_path)

    print(f"Pages extracted: {len(pages)}")

    for page in pages[:2]:

        print("\n--- PAGE", page["page"], "---")
        print(page["text"][:500])