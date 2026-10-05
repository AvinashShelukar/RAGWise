def split_text(text, chunk_size=1000, chunk_overlap=200):
    """
    Lightweight text splitter without LangChain.

    Splits text into overlapping chunks while trying
    to preserve paragraph and sentence boundaries.
    """

    text = text.strip()

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length
        )

        # Try to find a natural breaking point
        if end < text_length:

            candidates = [
                text.rfind("\n\n", start, end),
                text.rfind("\n", start, end),
                text.rfind(". ", start, end),
                text.rfind(" ", start, end)
            ]

            best_break = max(candidates)

            if best_break > start + (chunk_size // 2):
                end = best_break + 1

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        next_start = end - chunk_overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def chunk_documents(pages):
    """
    Split extracted PDF pages into smaller text chunks
    while preserving source and page information.
    """

    chunks = []

    for page in pages:

        page_chunks = split_text(
            page["text"],
            chunk_size=1000,
            chunk_overlap=200
        )

        for chunk in page_chunks:

            if chunk.strip():

                chunks.append({
                    "text": chunk.strip(),
                    "page": page["page"],
                    "source": page["source"]
                })

    return chunks