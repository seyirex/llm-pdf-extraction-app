"""V1 API router aggregation."""

from fastapi import APIRouter

from src.api.v1 import auth, upload, status, result, download, pdf

router = APIRouter(prefix="/api/v1", tags=["api"])

router.include_router(auth.router)
router.include_router(upload.router)
router.include_router(status.router)
router.include_router(result.router)
router.include_router(download.router)
router.include_router(pdf.router)
