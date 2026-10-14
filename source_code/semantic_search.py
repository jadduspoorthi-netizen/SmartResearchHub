import re

from source_code.database.connection import get_connection
from source_code.embedding_service import generate_query_embedding


# -------------------------------------------------------------------
# Domain intent detection
# -------------------------------------------------------------------

DOMAIN_KEYWORDS = {
    "machine learning": {
        "machine learning",
        "machine-learning",
        "ml",
    },
    "data science": {
        "data science",
        "data-science",
        "data analytics",
        "data analysis",
    },
    "deep learning": {
        "deep learning",
        "deep-learning",
        "neural network",
        "neural networks",
    },
    "database": {
        "database",
        "databases",
        "dbms",
        "sql",
        "query optimization",
        "database indexing",
        "indexing",
    },
    "artificial intelligence": {
        "artificial intelligence",
        "artificial-intelligence",
        "ai",
    },
}


RELATED_DOMAINS = {
    "machine learning": {
        "machine learning",
        "ml",
        "deep learning",
        "artificial intelligence",
        "ai",
    },
    "deep learning": {
        "deep learning",
        "machine learning",
        "ml",
        "artificial intelligence",
        "ai",
    },
    "data science": {
        "data science",
        "data analytics",
        "data analysis",
        "machine learning",
        "ml",
    },
    "database": {
        "database",
        "databases",
        "dbms",
        "sql",
    },
    "artificial intelligence": {
        "artificial intelligence",
        "ai",
        "machine learning",
        "ml",
        "deep learning",
    },
}


def _normalize_text(value: str) -> str:
    """
    Normalize text for keyword matching.
    """

    value = value.lower().strip()

    value = re.sub(
        r"[^a-z0-9\s-]",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value


def _detect_domain_intent(query: str) -> str | None:
    """
    Detect the strongest research-domain intent
    from the user's search query.
    """

    normalized_query = _normalize_text(query)

    # Check longer/more specific phrases first.
    detected_domains = []

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            normalized_keyword = _normalize_text(keyword)

            if normalized_keyword in normalized_query:
                detected_domains.append(
                    domain
                )
                break

    if not detected_domains:
        return None

    # Prefer the most specific domain when multiple
    # related terms occur.
    priority = [
        "deep learning",
        "machine learning",
        "data science",
        "database",
        "artificial intelligence",
    ]

    for domain in priority:
        if domain in detected_domains:
            return domain

    return detected_domains[0]


def _normalize_domain(domain: str | None) -> str:
    """
    Normalize a paper's stored domain.
    """

    if not domain:
        return ""

    return _normalize_text(domain)


def _domain_score(
    paper_domain: str | None,
    detected_domain: str | None,
) -> float:
    """
    Calculate a domain relevance score.

    Higher score = stronger domain match.
    """

    if not detected_domain:
        return 0.0

    domain = _normalize_domain(
        paper_domain
    )

    if not domain:
        return 0.0

    related_domains = RELATED_DOMAINS.get(
        detected_domain,
        set(),
    )

    # Exact domain match.
    if domain == detected_domain:
        return 1.0

    # Strong related-domain match.
    for related_domain in related_domains:
        if related_domain == domain:
            return 0.65

    # Stored domain may contain multiple labels.
    # Example:
    # "Machine Learning / Artificial Intelligence"
    for related_domain in related_domains:
        if related_domain in domain:
            return 0.55

    return 0.0


def _calculate_final_score(
    similarity: float,
    domain_score: float,
) -> float:
    """
    Combine semantic similarity with domain relevance.

    Semantic similarity remains the primary signal,
    while domain relevance helps correct closely related
    but incorrect research-domain results.
    """

    # Keep semantic similarity dominant.
    semantic_weight = 0.75
    domain_weight = 0.25

    return (
        similarity * semantic_weight
        + domain_score * domain_weight
    )


# -------------------------------------------------------------------
# Semantic search
# -------------------------------------------------------------------

def semantic_search(
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Search paper chunks using pgvector cosine similarity
    with domain-aware reranking.
    """

    query = query.strip()

    if not query:
        raise ValueError(
            "Search query cannot be empty."
        )

    if limit < 1:
        raise ValueError(
            "limit must be at least 1."
        )

    if limit > 50:
        limit = 50

    query_embedding = generate_query_embedding(
        query
    )

    detected_domain = _detect_domain_intent(
        query
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Retrieve more candidates than the final
        # requested limit so domain-aware reranking
        # has enough papers to work with.
        candidate_limit = min(
            max(limit * 5, 50),
            250,
        )

        cursor.execute(
            """
            SELECT
                p.id,
                p.title,
                p.authors,
                p.domain,
                p.year,
                p.filename,
                pc.id AS chunk_id,
                pc.chunk_index,
                pc.content,
                1 - (
                    pe.embedding <=> %s::vector
                ) AS similarity
            FROM paper_embeddings pe
            INNER JOIN paper_chunks pc
                ON pc.id = pe.chunk_id
            INNER JOIN papers p
                ON p.id = pc.paper_id
            ORDER BY pe.embedding <=> %s::vector
            LIMIT %s;
            """,
            (
                query_embedding,
                query_embedding,
                candidate_limit,
            ),
        )

        rows = cursor.fetchall()

        results = []

        for row in rows:
            similarity = float(
                row[9] or 0.0
            )

            domain_score = _domain_score(
                row[3],
                detected_domain,
            )

            final_score = _calculate_final_score(
                similarity=similarity,
                domain_score=domain_score,
            )

            results.append(
                {
                    "paper_id": row[0],
                    "title": row[1],
                    "authors": row[2],
                    "domain": row[3],
                    "year": row[4],
                    "filename": row[5],
                    "chunk_id": row[6],
                    "chunk_index": row[7],
                    "content": row[8],
                    "similarity": similarity,
                    "domain_score": domain_score,
                    "final_score": final_score,
                }
            )

        # Highest combined relevance first.
        results.sort(
            key=lambda item: item["final_score"],
            reverse=True,
        )

        # Return only the requested number of results.
        return results[:limit]

    finally:
        connection.close()


# -------------------------------------------------------------------
# Standalone test
# -------------------------------------------------------------------

if __name__ == "__main__":
    query = input(
        "Enter a semantic search query: "
    ).strip()

    if not query:
        print("No query entered.")
    else:
        try:
            detected_domain = _detect_domain_intent(
                query
            )

            print(
                f"\nDetected domain: "
                f"{detected_domain or 'None'}"
            )

            results = semantic_search(
                query,
                limit=15,
            )

            print(
                f"\nFound {len(results)} result(s).\n"
            )

            for index, result in enumerate(
                results,
                start=1,
            ):
                print(
                    f"{index}. "
                    f"{result['title']}"
                )

                print(
                    f"   Domain: "
                    f"{result['domain']}"
                )

                print(
                    f"   Similarity: "
                    f"{result['similarity']:.4f}"
                )

                print(
                    f"   Domain Score: "
                    f"{result['domain_score']:.4f}"
                )

                print(
                    f"   Final Score: "
                    f"{result['final_score']:.4f}"
                )

                print(
                    f"   Chunk: "
                    f"{result['chunk_index']}"
                )

                print()

        except Exception as error:
            print(
                "Semantic search failed:"
            )
            print(error)