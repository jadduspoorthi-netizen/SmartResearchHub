
from fastapi import APIRouter, Depends, HTTPException, status

from source_code.api_models import (
    AskRequest,
    AskResponse,
    SourceResponse,
)
from source_code.dependencies import get_current_user
from source_code.qa_service import (
    answer_research_question,
    format_qa_response,
)


router = APIRouter(
    prefix="/api/qa",
    tags=["Research Q&A"],
)


@router.post(
    "",
    response_model=AskResponse,
)
def ask_research_question(
    request: AskRequest,
    current_user: dict = Depends(get_current_user),
):
    # Only Premium users can use AI Research Q&A
    plan = str(current_user.get("plan", "free")).lower()

    if plan != "premium":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "AI Research Q&A is a Premium feature. "
                "Upgrade to Premium to unlock it."
            ),
        )

    try:
        result = answer_research_question(
            question=request.question,
            limit=request.limit,
        )

        response = format_qa_response(result)

        return AskResponse(
            question=response["question"],
            answer=response["answer"],
            sources=[
                SourceResponse(**source)
                for source in response["sources"]
            ],
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    except Exception as error:
        print("Research Q&A error:")
        print(error)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Research Q&A failed.",
        )


@router.get("/health")
def qa_health():
    return {
        "status": "ok",
        "service": "research-qa",
    }
