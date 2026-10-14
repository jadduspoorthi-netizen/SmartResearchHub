from typing import Optional

from source_code.paper_repository import get_all_papers
from source_code.semantic_search import semantic_search


def search_papers(
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Perform semantic search across indexed paper chunks.
    """

    query = query.strip()

    if not query:
        raise ValueError(
            "Search query cannot be empty."
        )

    if limit < 1:
        raise ValueError(
            "Search limit must be at least 1."
        )

    if limit > 50:
        limit = 50

    results = semantic_search(
        query=query,
        limit=limit,
    )

    return results


def search_repository(
    search: Optional[str] = None,
    domain: Optional[str] = None,
    year: Optional[int] = None,
) -> list[dict]:
    """
    Perform normal repository metadata filtering.
    """

    if search is not None:
        search = search.strip() or None

    if domain is not None:
        domain = domain.strip() or None

    return get_all_papers(
        search=search,
        domain=domain,
        year=year,
    )


def format_search_result(
    result: dict,
) -> dict:
    """
    Convert an internal semantic-search result
    into a clean API response object.
    """

    return {
        "paper_id": result.get("paper_id"),
        "title": result.get("title"),
        "authors": result.get("authors"),
        "domain": result.get("domain"),
        "year": result.get("year"),
        "filename": result.get("filename"),
        "chunk_id": result.get("chunk_id"),
        "chunk_index": result.get("chunk_index"),
        "content": result.get("content"),
        "similarity": round(
            float(result.get("similarity", 0.0)),
            4,
        ),
    }


def format_search_results(
    results: list[dict],
) -> list[dict]:
    """
    Format a complete semantic-search result set.
    """

    return [
        format_search_result(result)
        for result in results
    ]


if __name__ == "__main__":
    print(
        "Search service is ready."
    )
