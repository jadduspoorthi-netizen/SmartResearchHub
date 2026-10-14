from pathlib import Path
import re

import fitz


def validate_pdf(file_path: str | Path) -> Path:
    """
    Validate that the supplied path exists and points to a PDF file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only PDF files are supported."
        )

    return path


def clean_text(text: str) -> str:
    """
    Normalize extracted PDF text.
    """

    if not text:
        return ""

    # Normalize line endings.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive whitespace around lines.
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Collapse excessive blank lines.
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    # Remove spaces before punctuation.
    text = re.sub(
        r"\s+([,.;:!?])",
        r"\1",
        text,
    )

    return text.strip()


def extract_text_from_pdf(
    file_path: str | Path,
) -> str:
    """
    Extract readable text from every page of a PDF.
    """

    path = validate_pdf(file_path)

    document = None

    try:
        document = fitz.open(path)

        pages = []

        for page_number, page in enumerate(
            document,
            start=1,
        ):
            page_text = page.get_text("text")

            if page_text:
                cleaned_page = clean_text(page_text)

                if cleaned_page:
                    pages.append(
                        f"[Page {page_number}]\n"
                        f"{cleaned_page}"
                    )

        full_text = "\n\n".join(pages)
        full_text = clean_text(full_text)

        if not full_text:
            raise ValueError(
                "No readable text was found in the PDF. "
                "The document may be scanned or image-only."
            )

        return full_text

    finally:
        if document is not None:
            document.close()


def get_pdf_page_count(
    file_path: str | Path,
) -> int:
    """
    Return the number of pages in a PDF.
    """

    path = validate_pdf(file_path)

    document = None

    try:
        document = fitz.open(path)
        return len(document)

    finally:
        if document is not None:
            document.close()


if __name__ == "__main__":
    print(
        "PDF processor is ready. "
        "Provide a PDF path to test extraction."
    )
