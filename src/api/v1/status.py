"""Status endpoint — polls Celery task state and progress."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.api.dependencies import get_task_service, verify_api_key
from src.services.task_service import TaskService
from src.utils.responses import generate_response

router = APIRouter()


@router.get(
    "/status/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Poll task processing status",
    description="Returns current status and pipeline step "
    "for a previously submitted PDF processing task.",
)
def get_task_status(
    task_id: str,
    _auth: None = Depends(verify_api_key),
    task_service: TaskService = Depends(get_task_service),
) -> JSONResponse:
    """Get the current status of a processing task.

    Args:
        task_id: Celery task ID from the upload response.

    Returns:
        JSONResponse with current state and progress step.
    """
    task_status = task_service.get_status(task_id)

    return generate_response(
        success=True,
        data={
            "task_id": task_status.task_id,
            "status": task_status.state,
            "step": task_status.step,
        },
        status_code=status.HTTP_200_OK,
    )
