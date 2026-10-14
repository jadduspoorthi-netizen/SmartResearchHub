from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from source_code.dependencies import require_admin
from source_code.upload_service import (
    upload_and_ingest_paper,
)


router = APIRouter(
    prefix="/api/admin",
    tags=["Administration"],
)


@router.post(
    "/papers/upload",
)
def upload_paper(
    file: UploadFile = File(...),
    title: str = Form(...),
    authors: str | None = Form(default=None),
    domain: str | None = Form(default=None),
    year: int | None = Form(default=None),
    current_user: dict = Depends(
        require_admin
    ),
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A PDF file is required.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    title = title.strip()

    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paper title is required.",
        )

    if authors is not None:
        authors = authors.strip() or None

    if domain is not None:
        domain = domain.strip() or None

    if year is not None:
        if year < 1800 or year > 2100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Year must be between 1800 and 2100.",
            )

    try:
        result = upload_and_ingest_paper(
            source_file=file.file,
            original_filename=file.filename,
            title=title,
            authors=authors,
            domain=domain,
            year=year,
        )

        return {
            "message": "Research paper uploaded and indexed successfully.",
            "paper": result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    except Exception as error:
        print(
            "Paper upload error:"
        )
        print(error)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Research paper upload failed.",
        )

    finally:
        try:
            file.file.close()
        except Exception:
            pass


@router.get(
    "/health",
)
def admin_health(
    current_user: dict = Depends(
        require_admin
    ),
):
    return {
        "status": "ok",
        "service": "admin",
    }
