"""Task service — manages PDF upload, Celery task dispatch, and result retrieval."""

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from src.celery_app import celery_app
from src.config import settings
from src.tasks.process_pdf import process_pdf_task
from src.utils.exceptions import AppException
from src.utils.logger import get_logger

logger = get_logger()


@dataclass
class TaskStatus:
    """Represents the current status of a processing task."""

    task_id: str
    state: str
    step: Optional[str]


@dataclass
class TaskResult:
    """Represents the full result of a completed task."""

    task_id: str
    extracted: dict[str, Any]
    mapped: dict[str, Any]
    warnings: list[str]
    corrections: list[str]


class TaskService:
    """Handles PDF upload, task dispatching, status polling, and result retrieval."""

    def save_and_dispatch(self, content: bytes, original_filename: str) -> str:
        """Save a PDF to disk and dispatch a Celery processing task.

        Args:
            content: Raw bytes of the uploaded PDF file.
            original_filename: Original filename for logging.

        Returns:
            The generated task_id.
        """
        task_id = str(uuid.uuid4())

        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = upload_dir / f"{task_id}.pdf"
        pdf_path.write_bytes(content)

        output_path = Path(settings.output_dir) / f"{task_id}.txt"

        logger.info(f"PDF uploaded: {original_filename} → {pdf_path}")
        process_pdf_task.apply_async(
            args=[str(pdf_path), str(output_path)],
            task_id=task_id,
        )

        return task_id

    def get_status(self, task_id: str) -> TaskStatus:
        """Get the current status and step of a processing task.

        Args:
            task_id: Celery task ID.

        Returns:
            TaskStatus with current state and pipeline step.
        """
        result = celery_app.AsyncResult(task_id)

        step = None
        if result.state == "PROGRESS" and isinstance(result.info, dict):
            step = result.info.get("step")
        elif result.state == "SUCCESS":
            step = "completed"
        elif result.state == "FAILURE":
            step = "failed"

        return TaskStatus(task_id=task_id, state=result.state, step=step)

    def get_result(self, task_id: str) -> TaskResult:
        """Get the full result of a completed task.

        Args:
            task_id: Celery task ID.

        Returns:
            TaskResult with extracted/mapped data and diagnostics.

        Raises:
            TaskNotFoundError: If the task is pending or unknown.
            TaskFailedError: If the task failed.
            TaskNotCompleteError: If the task is still in progress.
        """
        result = celery_app.AsyncResult(task_id)

        if result.state == "PENDING":
            raise AppException(
                message="Task not found or still pending",
                status_code=404,
                error_code=AppException.TASK_NOT_FOUND,
            )

        if result.state == "FAILURE":
            raise AppException(
                message=f"Task failed: {result.result}",
                status_code=500,
                error_code=AppException.TASK_FAILED,
            )

        if result.state != "SUCCESS":
            raise AppException(
                message=f"Task not yet complete — current state: {result.state}",
                status_code=409,
                error_code=AppException.TASK_NOT_COMPLETE,
            )

        data = result.result
        if not isinstance(data, dict):
            raise AppException(
                message="Task result is malformed",
                status_code=500,
                error_code="internal_error",
            )

        extracted = data.get("extracted")
        mapped = data.get("mapped")
        if not isinstance(extracted, dict) or not isinstance(mapped, dict):
            raise AppException(
                message="Task result missing extracted/mapped payload",
                status_code=500,
                error_code="internal_error",
            )

        return TaskResult(
            task_id=task_id,
            extracted=extracted,
            mapped=mapped,
            warnings=data.get("warnings", []),
            corrections=data.get("corrections", []),
        )

    def get_download_path(self, task_id: str) -> Path:
        """Get the path to the generated TXT file for a completed task.

        Args:
            task_id: Celery task ID.

        Returns:
            Path to the generated TXT file.

        Raises:
            TaskNotFoundError: If the task is pending or unknown.
            TaskNotCompleteError: If the task is still in progress.
            FileNotFoundOnDiskError: If the output file does not exist.
        """
        result = celery_app.AsyncResult(task_id)

        if result.state == "PENDING":
            raise AppException(
                message="Task not found or still pending",
                status_code=404,
                error_code=AppException.TASK_NOT_FOUND,
            )

        if result.state != "SUCCESS":
            raise AppException(
                message=f"Task not yet complete — current state: {result.state}",
                status_code=409,
                error_code=AppException.TASK_NOT_COMPLETE,
            )

        data = result.result
        if not isinstance(data, dict) or "txt_path" not in data:
            raise AppException(
                message="Task result missing txt_path",
                status_code=500,
                error_code="internal_error",
            )

        txt_path = Path(data["txt_path"])

        if not txt_path.exists():
            raise AppException(
                message="Generated TXT file not found",
                status_code=404,
                error_code=AppException.FILE_NOT_FOUND,
            )

        return txt_path

    def get_pdf_path(self, task_id: str) -> Path:
        """Get the path to the uploaded PDF file for a task.

        Args:
            task_id: Celery task ID.

        Returns:
            Path to the uploaded PDF file.

        Raises:
            AppException: If the task is pending/unknown or the file is missing.
        """
        result = celery_app.AsyncResult(task_id)

        if result.state == "PENDING":
            raise AppException(
                message="Task not found or still pending",
                status_code=404,
                error_code=AppException.TASK_NOT_FOUND,
            )

        pdf_path = Path(settings.upload_dir) / f"{task_id}.pdf"

        if not pdf_path.exists():
            raise AppException(
                message="Uploaded PDF file not found",
                status_code=404,
                error_code=AppException.FILE_NOT_FOUND,
            )

        return pdf_path
