from pathlib import Path
from typing import Optional


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_DIR = (PROJECT_ROOT / "dataset").resolve()
UPLOAD_DIR = (DATASET_DIR / "uploads").resolve()


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _is_safe_dataset_path(path: Path) -> bool:
    """
    Ensure the resolved path stays inside the dataset directory.
    """

    try:
        path.relative_to(DATASET_DIR)
        return True
    except ValueError:
        return False


def _is_valid_pdf(path: Path) -> bool:
    """
    Check that the path exists, is a file, and is a PDF.
    """

    return (
        path.exists()
        and path.is_file()
        and path.suffix.lower() == ".pdf"
    )


# ============================================================
# PDF PATH RESOLUTION
# ============================================================

def resolve_pdf_path(
    file_path: str,
) -> Optional[Path]:
    """
    Resolve a stored PDF reference safely.

    Supported stored values include:

        dataset/uploads/example.pdf
        uploads/example.pdf
        example.pdf
        /absolute/path/to/project/dataset/uploads/example.pdf

    The resolved file must remain inside the application's
    dataset directory.
    """

    if not file_path:
        return None

    raw_value = str(file_path).strip()

    if not raw_value:
        return None

    # --------------------------------------------------------
    # 1. Absolute path
    # --------------------------------------------------------

    raw_path = Path(raw_value)

    if raw_path.is_absolute():
        absolute_path = raw_path.resolve()

        if (
            _is_safe_dataset_path(absolute_path)
            and _is_valid_pdf(absolute_path)
        ):
            return absolute_path

        return None

    # --------------------------------------------------------
    # 2. Normalize slash style
    # --------------------------------------------------------

    normalized = raw_value.replace("\\", "/").lstrip("/")

    # --------------------------------------------------------
    # 3. Try paths relative to the project root
    #
    # Example:
    #     dataset/uploads/paper.pdf
    # --------------------------------------------------------

    project_relative = (
        PROJECT_ROOT / normalized
    ).resolve()

    if (
        _is_safe_dataset_path(project_relative)
        and _is_valid_pdf(project_relative)
    ):
        return project_relative

    # --------------------------------------------------------
    # 4. Try paths relative to dataset
    #
    # Example:
    #     uploads/paper.pdf
    # --------------------------------------------------------

    dataset_relative = (
        DATASET_DIR / normalized
    ).resolve()

    if (
        _is_safe_dataset_path(dataset_relative)
        and _is_valid_pdf(dataset_relative)
    ):
        return dataset_relative

    # --------------------------------------------------------
    # 5. Try filename inside dataset/uploads
    #
    # Example:
    #     paper.pdf
    # --------------------------------------------------------

    filename_only = Path(normalized).name

    upload_file = (
        UPLOAD_DIR / filename_only
    ).resolve()

    if (
        _is_safe_dataset_path(upload_file)
        and _is_valid_pdf(upload_file)
    ):
        return upload_file

    # --------------------------------------------------------
    # Nothing matched
    # --------------------------------------------------------

    return None


# ============================================================
# PUBLIC PDF API
# ============================================================

def get_pdf_path(
    file_path: str,
) -> Path:
    """
    Return a validated PDF path.

    Raises FileNotFoundError when the stored PDF cannot
    safely be located.
    """

    path = resolve_pdf_path(file_path)

    if path is None:
        raise FileNotFoundError(
            "Research paper PDF could not be found."
        )

    return path


def is_uploaded_pdf(
    file_path: str,
) -> bool:
    """
    Check whether the resolved PDF belongs to dataset/uploads.
    """

    path = resolve_pdf_path(file_path)

    if path is None:
        return False

    try:
        path.relative_to(UPLOAD_DIR)
        return True
    except ValueError:
        return False


# ============================================================
# DIAGNOSTIC
# ============================================================

if __name__ == "__main__":
    print(
        "PDF service is ready."
    )

    print(
        f"Project root : {PROJECT_ROOT}"
    )

    print(
        f"Dataset dir  : {DATASET_DIR}"
    )

    print(
        f"Upload dir   : {UPLOAD_DIR}"
    )