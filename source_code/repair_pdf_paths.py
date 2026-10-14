from pathlib import Path

from source_code.database.connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = (
    PROJECT_ROOT / "dataset" / "uploads"
).resolve()


def normalize_name(value: str) -> str:
    return (
        Path(value).stem
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def repair_pdf_paths() -> None:
    if not UPLOAD_DIR.exists():
        raise FileNotFoundError(
            f"Upload directory not found: {UPLOAD_DIR}"
        )

    pdf_files = list(
        UPLOAD_DIR.glob("*.pdf")
    )

    if not pdf_files:
        print("No PDF files found.")
        return

    file_map = {}

    for pdf in pdf_files:
        file_map[
            normalize_name(pdf.name)
        ] = pdf

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, filename, file_path
                FROM papers
                ORDER BY id
                """
            )

            papers = cursor.fetchall()

            matched = 0
            skipped = 0

            for paper in papers:
                paper_id = paper[0]
                title = paper[1]
                filename = paper[2]
                file_path = paper[3]

                # Never overwrite a valid existing PDF mapping.
                if (
                    filename
                    and file_path
                    and Path(file_path).is_file()
                ):
                    skipped += 1
                    continue

                if not title:
                    skipped += 1
                    continue

                normalized_title = normalize_name(
                    title
                )

                pdf_path = file_map.get(
                    normalized_title
                )

                if pdf_path is None:
                    skipped += 1
                    continue

                cursor.execute(
                    """
                    UPDATE papers
                    SET
                        filename = %s,
                        file_path = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (
                        pdf_path.name,
                        str(pdf_path),
                        paper_id,
                    ),
                )

                matched += 1

                print(
                    f"Matched paper {paper_id}: "
                    f"{title} -> {pdf_path.name}"
                )

        connection.commit()

        print()
        print(
            f"Repair complete. "
            f"Matched: {matched}, "
            f"Skipped: {skipped}"
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    repair_pdf_paths()