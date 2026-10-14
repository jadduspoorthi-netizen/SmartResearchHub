from source_code.semantic_search import semantic_search


def get_rag_context(
    question: str,
    limit: int = 5,
) -> dict:
    """
    Retrieve relevant research-paper chunks for a question
    and prepare them as RAG context.
    """

    question = question.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    results = semantic_search(
        question,
        limit=limit,
    )

    context_parts = []
    sources = []

    for result in results:
        title = result.get(
            "title",
            "Unknown paper",
        )

        content = result.get(
            "content",
            "",
        )

        similarity = float(
            result.get(
                "similarity",
                0.0,
            )
        )

        context_parts.append(
            f"Paper: {title}\n"
            f"Similarity: {similarity:.4f}\n"
            f"Content:\n{content}"
        )

        sources.append(
            {
                "paper_id": result.get(
                    "paper_id"
                ),
                "title": title,
                "authors": result.get(
                    "authors"
                ),
                "domain": result.get(
                    "domain"
                ),
                "year": result.get(
                    "year"
                ),
                "chunk_index": result.get(
                    "chunk_index"
                ),
                "similarity": similarity,
            }
        )

    context = "\n\n---\n\n".join(
        context_parts
    )

    return {
        "question": question,
        "context": context,
        "sources": sources,
        "results": results,
    }


def build_context_text(
    results: list[dict],
) -> str:
    """
    Convert retrieved search results into
    a readable context string.
    """

    if not results:
        return ""

    parts = []

    for result in results:
        title = result.get(
            "title",
            "Unknown paper",
        )

        content = result.get(
            "content",
            "",
        )

        if not content:
            continue

        parts.append(
            f"Paper: {title}\n"
            f"{content}"
        )

    return "\n\n---\n\n".join(parts)


if __name__ == "__main__":
    print(
        "RAG service is ready."
    )
    print(
        "It retrieves semantic paper chunks "
        "and prepares research context."
    )
