"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import router as v1_router
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger()

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle."""
    
    logger.info("Starting up — creating upload/output directories")
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="PDF Data Extraction & Mapping",
    description="Extract data from German roller shutter order PDFs, "
    "map fields using deterministic rules, and output tab-separated TXT.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS setup: credentials cannot be used with wildcard origins.
raw_origins = [origin.strip() for origin in settings.cors_origins.split(",")]
use_wildcard_origins = "*" in raw_origins

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if use_wildcard_origins else raw_origins,
    allow_credentials=not use_wildcard_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(v1_router)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def serve_index() -> FileResponse:
    """Serve the single-page frontend."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint for container orchestration."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
