"""API dependency injection providers."""

import secrets

from fastapi import HTTPException, Request, status

from src.config import settings
from src.services.task_service import TaskService


def get_task_service() -> TaskService:
    """Provide a TaskService instance.

    Returns:
        TaskService instance for task management operations.
    """
    return TaskService()


def verify_api_key(request: Request) -> None:
    """Verify API key if auth is enabled.

    Accepts API key via configured header name or `api_key` query parameter.
    """
    if not settings.api_key_auth_enabled:
        return

    expected_key = settings.api_key.strip()
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key auth is enabled but API_KEY is not configured",
        )

    header_name = settings.api_key_header_name.strip().lower() or "x-api-key"
    provided_key = request.headers.get(header_name) or request.query_params.get("api_key", "")

    if not provided_key or not secrets.compare_digest(provided_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
