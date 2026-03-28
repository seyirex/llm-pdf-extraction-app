"""Result endpoint — returns extracted and mapped data as JSON."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.api.dependencies import get_task_service
from src.services.task_service import TaskService
from src.utils.exceptions import AppException
from src.utils.responses import generate_response

router = APIRouter()


@router.get(
    "/result/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Get processing results",
    description="Returns extracted data, mapped data, validation warnings, "
    "and corrections for a completed processing task.",
)
def get_task_result(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
) -> JSONResponse:
    """Get the full results of a completed processing task.

    Args:
        task_id: Celery task ID from the upload response.

    Returns:
        JSONResponse with extracted data, mapped data, and diagnostics.
    """
    try:
        task_result = task_service.get_result(task_id)
    except AppException as exc:
        return generate_response(
            success=False,
            error=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
        )

    return generate_response(
        success=True,
        data={
            "task_id": task_result.task_id,
            "extracted": task_result.extracted,
            "mapped": task_result.mapped,
            "warnings": task_result.warnings,
            "corrections": task_result.corrections,
        },
        status_code=status.HTTP_200_OK,
    )
