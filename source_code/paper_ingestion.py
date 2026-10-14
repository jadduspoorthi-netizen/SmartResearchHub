from pathlib import Path
from typing import Optional

from source_code.embedding_service import generate_embeddings
from source_code.kafka_service import publish_paper_uploaded
from source_code.mongo_service import save_paper_document
from source_code.paper_repository import (
    create_chunks_and_embeddings,
    create_paper,
    paper_title_exists,
)
from source_code.pdf_processor import extract_text_from_pdf
from source_code.text_chunker import chunk_text


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_DIR = PROJECT_ROOT / "dataset"
UPLOAD_DIR = DATASET_DIR / "uploads"


def validate_pdf_path(
    file_path: str | Path,
) -> Path:
    """
    Ensure the PDF exists and is inside the dataset directory.
    """

    path = Path(file_path).resolve()
    dataset_root = DATASET_DIR.resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"PDF path is not a file: {path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only PDF files are supported."
        )

    try:
        path.relative_to(dataset_root)
    except ValueError:
        raise ValueError(
            "PDF must be located inside the dataset directory."
        )

    return path


def ingest_single_paper(
    file_path: str | Path,
    title: str,
    authors: Optional[str] = None,
    domain: Optional[str] = None,
    year: Optional[int] = None,
) -> dict:
    """
    Ingest one research paper through the complete pipeline.
    """

    title = title.strip()

    if not title:
        raise ValueError(
            "Paper title cannot be empty."
        )

    path = validate_pdf_path(
        file_path
    )

    if paper_title_exists(title):
        raise ValueError(
            f"A paper with the title '{title}' "
            "already exists."
        )

    print(
        f"Processing PDF: {path.name}"
    )

    # ---------------------------------------------------------
    # 1. Extract text
    # ---------------------------------------------------------

    text = extract_text_from_pdf(
        path
    )

    if not text.strip():
        raise ValueError(
            "No readable text was extracted."
        )

    print(
        f"Extracted {len(text)} characters."
    )

    # ---------------------------------------------------------
    # 2. Create chunks
    # ---------------------------------------------------------

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError(
            "No text chunks were created."
        )

    print(
        f"Created {len(chunks)} text chunks."
    )

    # ---------------------------------------------------------
    # 3. Generate embeddings
    # ---------------------------------------------------------

    embeddings = generate_embeddings(
        chunks
    )

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            "Embedding count does not match chunk count."
        )

    print(
        f"Generated {len(embeddings)} embeddings."
    )

    # ---------------------------------------------------------
    # 4. Store paper metadata in PostgreSQL
    # ---------------------------------------------------------

    paper_id = create_paper(
        title=title,
        authors=authors,
        domain=domain,
        year=year,
        filename=path.name,
        file_path=str(path),
    )

    print(
        f"Created PostgreSQL paper ID: {paper_id}"
    )

    try:
        # -----------------------------------------------------
        # 5. Store chunks and embeddings
        # -----------------------------------------------------

        stored_chunks = create_chunks_and_embeddings(
            paper_id=paper_id,
            chunks=chunks,
            embeddings=embeddings,
        )

        print(
            f"Stored {stored_chunks} chunks and embeddings."
        )

        # -----------------------------------------------------
        # 6. Store document representation in MongoDB
        # -----------------------------------------------------

        try:
            save_paper_document(
                paper_id=paper_id,
                title=title,
                authors=authors,
                domain=domain,
                year=year,
                filename=path.name,
                file_path=str(path),
                chunks=chunks,
            )

            print(
                "MongoDB document stored."
            )

        except Exception as mongo_error:
            # PostgreSQL/pgvector remains the primary source
            # for semantic search. MongoDB failure is reported
            # but does not invalidate the stored paper.
            print(
                "MongoDB storage warning:"
            )
            print(mongo_error)

        # -----------------------------------------------------
        # 7. Publish Kafka event
        # -----------------------------------------------------

        kafka_result = publish_paper_uploaded(
            paper_id=paper_id,
            title=title,
            filename=path.name,
        )

        if kafka_result:
            print(
                "Kafka paper-upload event published."
            )
        else:
            print(
                "Kafka event skipped because Kafka "
                "is not currently available."
            )

        return {
            "success": True,
            "paper_id": paper_id,
            "title": title,
            "filename": path.name,
            "chunk_count": stored_chunks,
            "embedding_count": len(embeddings),
            "kafka_event": kafka_result,
        }

    except Exception:
        # The paper record and related data should not remain
        # partially stored if chunk/embedding insertion fails.
        #
        # Delete the paper. Foreign-key cascades remove
        # associated chunks and embeddings.
        try:
            from source_code.paper_repository import delete_paper

            delete_paper(paper_id)

        except Exception as cleanup_error:
            print(
                "Cleanup warning:"
            )
            print(cleanup_error)

        raise


def ensure_directories() -> None:
    """
    Ensure dataset directories exist.
    """

    DATASET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


if __name__ == "__main__":
    ensure_directories()

    print(
        "Paper ingestion service is ready."
    )

    print(
        f"Dataset directory: {DATASET_DIR}"
    )

    print(
        f"Upload directory: {UPLOAD_DIR}"
    )

    print(
        "\nUse ingest_single_paper() "
        "from the application or upload pipeline "
        "to process a PDF."
    )
