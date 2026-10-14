from pathlib import Path
from typing import Optional

from source_code.chunk_repository import count_chunks_by_paper_id
from source_code.mongo_service import delete_paper_document
from source_code.paper_repository import (
    delete_paper,
    get_all_papers,
    get_paper_by_id,
    get_domains,
    paper_title_exists,
    update_paper,
)
from source_code.upload_service import delete_uploaded_file


def list_papers(
    search: Optional[str] = None,
    domain: Optional[str] = None,
    year: Optional[int] = None,
) -> list[dict]:
    """
    Return papers matching the supplied repository filters.
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


def get_paper_details(
    paper_id: int,
) -> Optional[dict]:
    """
    Return paper metadata together with its chunk count.
    """

    paper = get_paper_by_id(paper_id)

    if paper is None:
        return None

    paper["chunk_count"] = count_chunks_by_paper_id(
        paper_id
    )

    return paper


def list_domains() -> list[str]:
    """
    Return all available paper domains.
    """

    return get_domains()


def update_paper_metadata(
    paper_id: int,
    title: Optional[str] = None,
    authors: Optional[str] = None,
    domain: Optional[str] = None,
    year: Optional[int] = None,
) -> Optional[dict]:
    """
    Update paper metadata.

    Semantic chunks and embeddings are preserved because
    metadata changes do not alter the paper's extracted content.
    """

    current = get_paper_by_id(paper_id)

    if current is None:
        return None

    if title is not None:
        title = title.strip()

        if not title:
            raise ValueError(
                "Paper title cannot be empty."
            )

        if paper_title_exists(
            title,
            exclude_paper_id=paper_id,
        ):
            raise ValueError(
                f"A paper with the title '{title}' "
                "already exists."
            )

    if authors is not None:
        authors = authors.strip() or None

    if domain is not None:
        domain = domain.strip() or None

    if year is not None:
        if year < 1800 or year > 2100:
            raise ValueError(
                "Year must be between 1800 and 2100."
            )

    return update_paper(
        paper_id=paper_id,
        title=title,
        authors=authors,
        domain=domain,
        year=year,
    )


def delete_paper_completely(
    paper_id: int,
) -> bool:
    """
    Delete a paper from PostgreSQL, MongoDB,
    and its uploaded PDF when applicable.
    """

    paper = get_paper_by_id(paper_id)

    if paper is None:
        return False

    file_path = paper.get("file_path")

    deleted = delete_paper(
        paper_id
    )

    if not deleted:
        return False

    try:
        delete_paper_document(
            paper_id
        )
    except Exception as error:
        print(
            "MongoDB deletion warning:"
        )
        print(error)

    if file_path:
        try:
            upload_root = (
                Path(__file__).resolve().parent.parent
                / "dataset"
                / "uploads"
            ).resolve()

            candidate = Path(
                file_path
            ).resolve()

            candidate.relative_to(
                upload_root
            )

            delete_uploaded_file(
                candidate
            )

        except ValueError:
            pass

        except Exception as error:
            print(
                "PDF deletion warning:"
            )
            print(error)

    return True


if __name__ == "__main__":
    print(
        "Paper service is ready."
    )