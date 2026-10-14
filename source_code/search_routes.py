
from fastapi import APIRouter, Depends, HTTPException, status

from source_code.api_models import (
    SearchRequest,
    SearchResultResponse,
)
from source_code.dependencies import get_current_user
from source_code.search_service import (
    format_search_results,
    search_papers,
)
from source_code.database.connection import get_connection


router = APIRouter(
    prefix="/api/search",
    tags=["Semantic Search"],
)

# Free users can search 10 times per day
FREE_DAILY_SEARCH_LIMIT = 20


def consume_search_quota(user_id: int) -> int:
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO daily_usage (
                    user_id, usage_date, search_count
                )
                VALUES (%s, CURRENT_DATE, 1)
                ON CONFLICT (user_id, usage_date)
                DO UPDATE SET
                    search_count = daily_usage.search_count + 1
                WHERE daily_usage.search_count < %s
                RETURNING search_count;
                """,
                (user_id, FREE_DAILY_SEARCH_LIMIT),
            )

            row = cursor.fetchone()

            if row is None:
                connection.commit()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        "You've reached your 20 free searches for today. "
    "Upgrade to Premium for unlimited searches."
                    ),
                )

            connection.commit()
            return FREE_DAILY_SEARCH_LIMIT - row[0]

    except HTTPException:
        raise
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@router.post("", response_model=list[SearchResultResponse])
def semantic_paper_search(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        plan = str(current_user.get("plan", "free")).lower()

        if plan != "premium":
            consume_search_quota(current_user["id"])

        results = search_papers(
            query=request.query,
            limit=request.limit,
        )

        return format_search_results(results)

    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    except Exception as error:
        print("Semantic search error:")
        print(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Semantic search failed.",
        )


@router.get("/usage")
def get_search_usage(
    current_user: dict = Depends(get_current_user),
):
    plan = str(current_user.get("plan", "free")).lower()

    if plan == "premium":
        return {
            "plan": "premium",
            "searches_used": None,
            "searches_remaining": None,
            "daily_limit": None,
            "qa_enabled": True,
        }

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT search_count
                FROM daily_usage
                WHERE user_id = %s
                  AND usage_date = CURRENT_DATE
                """,
                (current_user["id"],),
            )

            row = cursor.fetchone()
            searches_used = row[0] if row else 0

            return {
                "plan": "free",
                "searches_used": searches_used,
                "searches_remaining": max(
                    0,
                    FREE_DAILY_SEARCH_LIMIT - searches_used,
                ),
                "daily_limit": FREE_DAILY_SEARCH_LIMIT,
                "qa_enabled": False,
            }
    finally:
        connection.close()


@router.get("/health")
def search_health():
    return {
        "status": "ok",
        "service": "semantic-search",
    }
