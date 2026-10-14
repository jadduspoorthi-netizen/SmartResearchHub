DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Example:
        chunk_size = 1000
        overlap = 200

    The next chunk starts 800 characters after the previous
    chunk starts, so 200 characters are shared.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    text = text.strip()

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(
            start + chunk_size,
            text_length,
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


def validate_chunks(chunks: list[str]) -> None:
    """
    Validate a generated chunk collection.
    """

    if not isinstance(chunks, list):
        raise TypeError("chunks must be a list.")

    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, str):
            raise TypeError(
                f"Chunk {index} must be a string."
            )

        if not chunk.strip():
            raise ValueError(
                f"Chunk {index} cannot be empty."
            )


if __name__ == "__main__":
    sample_text = (
        "SmartResearch Hub processes research papers, "
        "creates semantic chunks, generates embeddings, "
        "and stores them for intelligent retrieval."
    )

    chunks = chunk_text(
        sample_text,
        chunk_size=40,
        overlap=10,
    )

    validate_chunks(chunks)

    print(f"Created {len(chunks)} chunks.")

    for index, chunk in enumerate(chunks):
        print(f"\nChunk {index}:")
        print(chunk)
