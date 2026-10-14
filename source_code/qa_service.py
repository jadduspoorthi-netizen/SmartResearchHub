from source_code.local_answer_service import (
    generate_local_answer,
)
from source_code.rag_service import (
    get_rag_context,
)


def answer_research_question(
    question: str,
    limit: int = 5,
) -> dict:
    """
    Answer a research question using:

    Question
        ↓
    Semantic retrieval
        ↓
    Relevant paper chunks
        ↓
    RAG context
        ↓
    Local extractive answer
    """

    question = question.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    if limit < 1:
        raise ValueError(
            "Result limit must be at least 1."
        )

    if limit > 20:
        limit = 20

    rag_data = get_rag_context(
        question=question,
        limit=limit,
    )

    answer = generate_local_answer(
        question=question,
        context=rag_data["context"],
        max_sentences=5,
    )

    return {
        "question": question,
        "answer": answer,
        "sources": rag_data["sources"],
        "retrieved_results": rag_data["results"],
    }


def format_qa_response(
    result: dict,
) -> dict:
    """
    Return a clean API-friendly Q&A response.
    """

    return {
        "question": result.get("question"),
        "answer": result.get("answer"),
        "sources": result.get("sources", []),
    }


if __name__ == "__main__":
    print(
        "Q&A service is ready."
    )
