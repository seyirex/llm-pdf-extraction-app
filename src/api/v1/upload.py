"""Upload endpoint — accepts PDF files and dispatches processing tasks."""

from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import JSONResponse

from src.api.dependencies import get_task_service
from src.config import settings
from src.services.task_service import TaskService
from src.utils.responses import generate_response

router = APIRouter()


@router.post(
    "/upload",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a PDF for processing",
    description="Accepts a PDF file, saves it, and dispatches an async "
    "processing task. Returns a task_id for status polling.",
)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to process"),
    task_service: TaskService = Depends(get_task_service),
) -> JSONResponse:
    """Upload a PDF file and start async processing.

    Args:
        file: The uploaded PDF file.

    Returns:
        JSONResponse with task_id for status tracking.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return generate_response(
            success=False,
            error="bad_request",
            message="File must be a PDF",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if file.content_type and file.content_type != "application/pdf":
        return generate_response(
            success=False,
            error="bad_request",
            message="File content type must be application/pdf",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    content = await file.read()
    max_upload_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_upload_bytes:
        return generate_response(
            success=False,
            error="payload_too_large",
            message=f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )

    task_id = task_service.save_and_dispatch(content, file.filename)

    return generate_response(
        success=True,
        data={"task_id": task_id},
        message="PDF uploaded and processing started",
        status_code=status.HTTP_202_ACCEPTED,
    )
