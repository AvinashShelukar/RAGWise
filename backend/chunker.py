from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(pages):
    """
    Split extracted PDF pages into smaller text chunks
    while preserving source and page information.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = []

    for page in pages:

        page_chunks = splitter.split_text(
            page["text"]
        )

        for chunk in page_chunks:

            if chunk.strip():

                chunks.append({
                    "text": chunk.strip(),
                    "page": page["page"],
                    "source": page["source"]
                })

    return chunks