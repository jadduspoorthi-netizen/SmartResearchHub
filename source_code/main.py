from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from source_code.admin_routes import router as admin_router
from source_code.auth_routes import router as auth_router
from source_code.health_routes import router as health_router
from source_code.paper_routes import router as paper_router
from source_code.qa_routes import router as qa_router
from source_code.search_routes import router as search_router


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"


app = FastAPI(
    title="SmartResearch Hub",
    description=(
        "AI-powered semantic research repository "
        "with semantic search and research Q&A."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router
)

app.include_router(
    auth_router
)

app.include_router(
    paper_router
)

app.include_router(
    search_router
)

app.include_router(
    qa_router
)

app.include_router(
    admin_router
)


if FRONTEND_DIR.exists():
    app.mount(
        "/frontend",
        StaticFiles(
            directory=FRONTEND_DIR,
            html=True,
        ),
        name="frontend",
    )


@app.get(
    "/",
    tags=["Application"],
)
def root():
    return {
        "application": "SmartResearch Hub",
        "version": "1.0.0",
        "status": "running",
        "message": (
            "SmartResearch Hub API is running."
        ),
        "documentation": "/docs",
    }


@app.get(
    "/api",
    tags=["Application"],
)
def api_root():
    return {
        "application": "SmartResearch Hub",
        "status": "ok",
        "endpoints": {
            "authentication": "/api/auth",
            "repository": "/api/papers",
            "semantic_search": "/api/search",
            "research_qa": "/api/qa",
            "administration": "/api/admin",
            "health": "/api/health",
            "documentation": "/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "source_code.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
