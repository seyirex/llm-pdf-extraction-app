"""Download endpoint — serves generated TXT file as attachment."""

from typing import Union

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse, JSONResponse

from src.api.dependencies import get_task_service
from src.services.task_service import TaskService
from src.utils.exceptions import AppException
from src.utils.responses import generate_response

router = APIRouter()


@router.get(
    "/download/{task_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Download generated TXT file",
    description="Serves the generated tab-separated TXT file "
    "as a downloadable attachment for a completed task.",
)
def download_txt(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
) -> Union[FileResponse, JSONResponse]:
    """Download the generated TXT file for a completed task.

    Args:
        task_id: Celery task ID from the upload response.

    Returns:
        FileResponse with the TXT file, or JSONResponse on error.
    """
    try:
        txt_path = task_service.get_download_path(task_id)
    except AppException as exc:
        return generate_response(
            success=False,
            error=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
        )

    return FileResponse(
        path=str(txt_path),
        filename=f"output_{task_id}.txt",
        media_type="text/plain",
    )
