import re
from collections import Counter


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "what",
    "when",
    "where",
    "which",
    "who",
    "with",
}


def tokenize(text: str) -> list[str]:
    """
    Convert text into normalized word tokens.
    """

    if not text:
        return []

    words = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower(),
    )

    return [
        word
        for word in words
        if word not in STOPWORDS
    ]


def split_sentences(text: str) -> list[str]:
    """
    Split text into simple readable sentences.
    """

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def score_sentence(
    sentence: str,
    question_terms: set[str],
) -> float:
    """
    Score a sentence according to its overlap
    with the question terms.
    """

    sentence_terms = tokenize(sentence)

    if not sentence_terms:
        return 0.0

    overlap = sum(
        1
        for term in sentence_terms
        if term in question_terms
    )

    frequency = Counter(sentence_terms)

    repeated_terms = sum(
        count - 1
        for count in frequency.values()
        if count > 1
    )

    return (
        overlap * 2.0
        + repeated_terms * 0.1
    )


def generate_local_answer(
    question: str,
    context: str,
    max_sentences: int = 5,
) -> str:
    """
    Generate an extractive answer from retrieved context.

    This method does not call an external AI service.
    """

    question = question.strip()
    context = context.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    if not context:
        return (
            "I could not find enough relevant "
            "research content to answer this question."
        )

    if max_sentences < 1:
        max_sentences = 1

    question_terms = set(
        tokenize(question)
    )

    sentences = split_sentences(context)

    if not sentences:
        return (
            "Relevant research content was found, "
            "but it could not be converted into "
            "a readable answer."
        )

    scored_sentences = []

    for index, sentence in enumerate(
        sentences
    ):
        score = score_sentence(
            sentence,
            question_terms,
        )

        scored_sentences.append(
            (
                score,
                index,
                sentence,
            )
        )

    scored_sentences.sort(
        key=lambda item: (
            item[0],
            -item[1],
        ),
        reverse=True,
    )

    selected = [
        item
        for item in scored_sentences
        if item[0] > 0
    ][:max_sentences]

    if not selected:
        selected = scored_sentences[
            :max_sentences
        ]

    selected.sort(
        key=lambda item: item[1]
    )

    answer_sentences = [
        item[2]
        for item in selected
    ]

    return " ".join(
        answer_sentences
    )


def generate_answer_from_results(
    question: str,
    results: list,
    max_sentences: int = 5,
) -> str:
    """
    Generate an answer directly from semantic-search results.

    Supports both dictionary results and tuple-style results.
    """

    context_parts = []

    for result in results:
        if isinstance(result, dict):
            content = result.get(
                "content",
                "",
            )

        elif isinstance(result, (tuple, list)):
            # Expected tuple layout:
            # paper_id, title, domain, year,
            # chunk_index, content, similarity
            content = (
                result[5]
                if len(result) > 5
                else ""
            )

        else:
            content = ""

        if content:
            context_parts.append(
                str(content)
            )

    context = "\n\n".join(
        context_parts
    )

    return generate_local_answer(
        question=question,
        context=context,
        max_sentences=max_sentences,
    )


if __name__ == "__main__":
    sample_question = (
        "What is semantic search?"
    )

    sample_context = """
    Semantic search retrieves documents based on
    meaning rather than exact keyword matching.
    Research repositories can use embeddings to
    represent documents as numerical vectors.
    Similar vectors indicate related semantic meaning.
    """

    answer = generate_local_answer(
        sample_question,
        sample_context,
    )

    print("Question:")
    print(sample_question)

    print("\nAnswer:")
    print(answer)
