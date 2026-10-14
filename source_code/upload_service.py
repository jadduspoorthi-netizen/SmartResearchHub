from pathlib import Path
from typing import Optional
import shutil
import uuid

from source_code.paper_ingestion import ingest_single_paper


PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = PROJECT_ROOT / "dataset" / "uploads"


def ensure_upload_directory() -> None:
    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def save_uploaded_pdf(
    source_file,
    original_filename: str,
) -> Path:
    """
    Save an uploaded PDF into dataset/uploads.

    A unique filename is generated to prevent collisions.
    """

    ensure_upload_directory()

    if not original_filename:
        raise ValueError(
            "Original filename is required."
        )

    original_path = Path(
        original_filename
    )

    if original_path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only PDF files are allowed."
        )

    safe_name = (
        original_path.name
        .replace(" ", "_")
    )

    unique_name = (
        f"{uuid.uuid4().hex[:12]}_{safe_name}"
    )

    destination = (
        UPLOAD_DIR / unique_name
    )

    with destination.open("wb") as output_file:
        shutil.copyfileobj(
            source_file,
            output_file,
        )

    return destination


def upload_and_ingest_paper(
    source_file,
    original_filename: str,
    title: str,
    authors: Optional[str] = None,
    domain: Optional[str] = None,
    year: Optional[int] = None,
) -> dict:
    """
    Save an uploaded PDF and send it through
    the complete paper-ingestion pipeline.
    """

    saved_path = save_uploaded_pdf(
        source_file=source_file,
        original_filename=original_filename,
    )

    try:
        result = ingest_single_paper(
            file_path=saved_path,
            title=title,
            authors=authors,
            domain=domain,
            year=year,
        )

        return result

    except Exception:
        # If ingestion fails, remove the uploaded file
        # so failed uploads do not accumulate.
        try:
            if saved_path.exists():
                saved_path.unlink()
        except Exception as cleanup_error:
            print(
                "Upload cleanup warning:"
            )
            print(cleanup_error)

        raise


def delete_uploaded_file(
    file_path: str | Path,
) -> bool:
    """
    Delete a PDF file stored in the upload directory.
    """

    path = Path(
        file_path
    ).resolve()

    upload_root = UPLOAD_DIR.resolve()

    try:
        path.relative_to(upload_root)
    except ValueError:
        raise ValueError(
            "File is outside the upload directory."
        )

    if not path.exists():
        return False

    if not path.is_file():
        raise ValueError(
            "Upload path is not a file."
        )

    path.unlink()

    return True


if __name__ == "__main__":
    ensure_upload_directory()

    print(
        "Upload service is ready."
    )

    print(
        f"Upload directory: {UPLOAD_DIR}"
    )

