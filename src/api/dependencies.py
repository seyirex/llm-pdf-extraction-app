"""API dependency injection providers."""

from src.services.task_service import TaskService


def get_task_service() -> TaskService:
    """Provide a TaskService instance.

    Returns:
        TaskService instance for task management operations.
    """
    return TaskService()
