from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from source_code.api_models import (
    PaperResponse,
    PaperUpdateRequest,
)
from source_code.dependencies import (
    get_current_user,
    require_admin,
)
from source_code.paper_service import (
    delete_paper_completely,
    get_paper_details,
    list_domains,
    list_papers,
    update_paper_metadata,
)
from source_code.pdf_service import get_pdf_path


router = APIRouter(
    prefix="/api/papers",
    tags=["Research Repository"],
)


@router.get(
    "",
    response_model=list[PaperResponse],
)
def get_papers(
    search: str | None = None,
    domain: str | None = None,
    year: int | None = None,
    current_user: dict = Depends(
        get_current_user
    ),
):
    return list_papers(
        search=search,
        domain=domain,
        year=year,
    )


@router.get(
    "/domains",
    response_model=list[str],
)
def get_paper_domains(
    current_user: dict = Depends(
        get_current_user
    ),
):
    return list_domains()


@router.get(
    "/{paper_id}",
)
def get_paper(
    paper_id: int,
    current_user: dict = Depends(
        get_current_user
    ),
):
    paper = get_paper_details(
        paper_id
    )

    if paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research paper not found.",
        )

    return paper


@router.get(
    "/{paper_id}/pdf",
)
def get_paper_pdf(
    paper_id: int,
    current_user: dict = Depends(
        get_current_user
    ),
):
    paper = get_paper_details(
        paper_id
    )

    if paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research paper not found.",
        )

    file_path = paper.get(
        "file_path"
    )

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file is not associated with this paper.",
        )

    try:
        pdf_path = get_pdf_path(
            file_path
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research paper PDF could not be found.",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=Path(pdf_path).name,
    )


@router.put(
    "/{paper_id}",
)
def update_paper(
    paper_id: int,
    request: PaperUpdateRequest,
    current_user: dict = Depends(
        require_admin
    ),
):
    try:
        updated = update_paper_metadata(
            paper_id=paper_id,
            title=request.title,
            authors=request.authors,
            domain=request.domain,
            year=request.year,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research paper not found.",
        )

    return {
        "message": "Research paper updated successfully.",
        "paper": updated,
    }


@router.delete(
    "/{paper_id}",
)
def remove_paper(
    paper_id: int,
    current_user: dict = Depends(
        require_admin
    ),
):
    deleted = delete_paper_completely(
        paper_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research paper not found.",
        )

    return {
        "message": "Research paper deleted successfully.",
        "paper_id": paper_id,
    }
