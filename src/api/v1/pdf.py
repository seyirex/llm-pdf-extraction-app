"""PDF preview endpoint — serves uploaded PDF inline for browser rendering."""

from fastapi import APIRouter, Depends, Response, status
from starlette.responses import FileResponse

from src.api.dependencies import get_task_service, verify_api_key
from src.services.task_service import TaskService
from src.utils.exceptions import AppException
from src.utils.responses import PDF_FILE_RESPONSES, generate_response

router = APIRouter()


@router.get(
    "/pdf/{task_id}",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
    responses=PDF_FILE_RESPONSES,
    summary="Preview uploaded PDF",
    description="Serves the uploaded PDF file inline for browser rendering.",
)
def preview_pdf(
    task_id: str,
    _auth: None = Depends(verify_api_key),
    task_service: TaskService = Depends(get_task_service),
) -> Response:
    """Return the uploaded PDF for inline browser preview.

    Args:
        task_id: Celery task ID from the upload response.

    Returns:
        FileResponse with the PDF (inline), or JSONResponse on error.
    """
    try:
        pdf_path = task_service.get_pdf_path(task_id)
    except AppException as exc:
        return generate_response(
            success=False,
            error=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
        )

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
    )
