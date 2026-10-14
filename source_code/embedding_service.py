import os
from functools import lru_cache

import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


load_dotenv()


MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2",
)

EMBEDDING_DIMENSION = int(
    os.getenv(
        "EMBEDDING_DIMENSION",
        "384",
    )
)


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """
    Load and cache the sentence-transformer model.
    """

    return SentenceTransformer(MODEL_NAME)


def get_embedding_dimension() -> int:
    """
    Return the configured embedding dimension.
    """

    return EMBEDDING_DIMENSION


def get_model_name() -> str:
    """
    Return the configured embedding model name.
    """

    return MODEL_NAME


def generate_embeddings(
    texts: list[str],
) -> np.ndarray:
    """
    Generate normalized embeddings for a list of texts.
    """

    if not isinstance(texts, list):
        raise TypeError("texts must be a list.")

    if not texts:
        return np.empty(
            (0, EMBEDDING_DIMENSION),
            dtype=np.float32,
        )

    for index, text in enumerate(texts):
        if not isinstance(text, str):
            raise TypeError(
                f"Text at index {index} must be a string."
            )

        if not text.strip():
            raise ValueError(
                f"Text at index {index} cannot be empty."
            )

    model = get_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32,
    )

    if embeddings.ndim != 2:
        raise RuntimeError(
            "Embedding model returned an invalid shape."
        )

    if embeddings.shape[0] != len(texts):
        raise RuntimeError(
            "Embedding count does not match text count."
        )

    if embeddings.shape[1] != EMBEDDING_DIMENSION:
        raise RuntimeError(
            "Embedding dimension mismatch: "
            f"expected {EMBEDDING_DIMENSION}, "
            f"received {embeddings.shape[1]}."
        )

    return embeddings


def generate_query_embedding(
    query: str,
) -> list[float]:
    """
    Generate one normalized embedding for a search query.
    """

    if not isinstance(query, str):
        raise TypeError("query must be a string.")

    query = query.strip()

    if not query:
        raise ValueError("query cannot be empty.")

    embeddings = generate_embeddings([query])

    return embeddings[0].tolist()


def save_embeddings(
    embeddings: np.ndarray,
    output_path: str,
) -> None:
    """
    Save embeddings as a NumPy .npy file.
    """

    if not isinstance(embeddings, np.ndarray):
        raise TypeError(
            "embeddings must be a NumPy array."
        )

    if embeddings.ndim != 2:
        raise ValueError(
            "embeddings must be a 2-dimensional array."
        )

    if embeddings.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError(
            "Embedding dimension does not match configuration."
        )

    np.save(
        output_path,
        embeddings,
    )


if __name__ == "__main__":
    print(
        f"Embedding model: {MODEL_NAME}"
    )

    print(
        f"Embedding dimension: "
        f"{EMBEDDING_DIMENSION}"
    )

    print("Loading model...")

    embeddings = generate_embeddings(
        [
            "SmartResearch Hub stores research papers.",
            "Semantic search retrieves relevant research.",
        ]
    )

    print(
        "Generated embedding shape:",
        embeddings.shape,
    )

    query_embedding = generate_query_embedding(
        "semantic research search"
    )

    print(
        "Query embedding length:",
        len(query_embedding),
    )
