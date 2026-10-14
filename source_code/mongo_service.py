import os
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017",
)

MONGO_DB = os.getenv(
    "MONGO_DB",
    "smartresearchhub",
)


_client: Optional[MongoClient] = None


def get_mongo_client() -> MongoClient:
    """
    Create and cache the MongoDB client.
    """

    global _client

    if _client is None:
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=3000,
        )

    return _client


def get_database():
    """
    Return the SmartResearch Hub MongoDB database.
    """

    client = get_mongo_client()

    return client[MONGO_DB]


def get_papers_collection():
    """
    Return the papers collection.
    """

    return get_database()["papers"]


def test_mongo_connection() -> bool:
    """
    Test whether MongoDB is reachable.
    """

    try:
        client = get_mongo_client()

        client.admin.command(
            "ping"
        )

        return True

    except Exception:
        return False


def save_paper_document(
    paper_id: int,
    title: str,
    authors: Optional[str],
    domain: Optional[str],
    year: Optional[int],
    filename: Optional[str],
    file_path: Optional[str],
    chunks: Optional[list[str]] = None,
) -> None:
    """
    Insert or update a paper document in MongoDB.
    """

    collection = get_papers_collection()

    document = {
        "paper_id": paper_id,
        "title": title,
        "authors": authors,
        "domain": domain,
        "year": year,
        "filename": filename,
        "file_path": file_path,
        "chunks": chunks or [],
        "updated_at": datetime.now(
            timezone.utc
        ),
    }

    collection.update_one(
        {
            "paper_id": paper_id,
        },
        {
            "$set": document,
            "$setOnInsert": {
                "created_at": datetime.now(
                    timezone.utc
                ),
            },
        },
        upsert=True,
    )


def get_paper_document(
    paper_id: int,
) -> Optional[dict]:
    """
    Retrieve a paper document by PostgreSQL paper ID.
    """

    collection = get_papers_collection()

    return collection.find_one(
        {
            "paper_id": paper_id,
        }
    )


def delete_paper_document(
    paper_id: int,
) -> None:
    """
    Delete a paper document from MongoDB.
    """

    collection = get_papers_collection()

    collection.delete_one(
        {
            "paper_id": paper_id,
        }
    )


if __name__ == "__main__":
    if test_mongo_connection():
        print(
            "MongoDB connection successful."
        )
    else:
        print(
            "MongoDB is not currently reachable."
        )
