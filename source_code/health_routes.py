from fastapi import APIRouter

from source_code.mongo_service import test_mongo_connection


router = APIRouter(
    prefix="/api/health",
    tags=["System Health"],
)


@router.get("")
def health_check():
    mongo_available = test_mongo_connection()

    return {
        "status": "ok",
        "application": "SmartResearch Hub",
        "services": {
            "api": "ok",
            "postgresql": "configured",
            "semantic_search": "ready",
            "rag": "ready",
            "mongodb": (
                "ok"
                if mongo_available
                else "unavailable"
            ),
        },
    }


@router.get("/mongodb")
def mongodb_health():
    mongo_available = test_mongo_connection()

    return {
        "service": "mongodb",
        "status": (
            "ok"
            if mongo_available
            else "unavailable"
        ),
    }
