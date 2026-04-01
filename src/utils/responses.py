"""
Response utilities for consistent API responses.
"""

from typing import Any, Optional
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class StandardResponse(BaseModel):
    """Standard response envelope for all API endpoints."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    exceptionError: Optional[str] = None
    message: Optional[str] = None


DOWNLOAD_FILE_RESPONSES: dict[int, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "content": {"text/plain": {}},
        "description": "Generated TXT file",
    },
    status.HTTP_401_UNAUTHORIZED: {
        "model": StandardResponse,
        "description": "Missing or invalid API key",
    },
    status.HTTP_404_NOT_FOUND: {
        "model": StandardResponse,
        "description": "Task or generated file not found",
    },
    status.HTTP_409_CONFLICT: {
        "model": StandardResponse,
        "description": "Task has not completed yet",
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "model": StandardResponse,
        "description": "Task result is malformed or server is misconfigured",
    },
}


PDF_FILE_RESPONSES: dict[int, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "content": {"application/pdf": {}},
        "description": "Uploaded PDF file",
    },
    status.HTTP_401_UNAUTHORIZED: {
        "model": StandardResponse,
        "description": "Missing or invalid API key",
    },
    status.HTTP_404_NOT_FOUND: {
        "model": StandardResponse,
        "description": "Task or uploaded PDF not found",
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "model": StandardResponse,
        "description": "Server is misconfigured",
    },
}


def generate_response(
    success: bool = True,
    data: Optional[Any] = None,
    error: Optional[str] = None,
    exception_error: Optional[str] = None,
    message: Optional[str] = None,
    status_code: int = 200
) -> JSONResponse:
    """
    Generate a consistent JSON response for all API endpoints.

    Args:
        success: Whether the operation was successful
        data: The data payload to return
        error: General error message (e.g., "bad_request", "unauthorized")
        exception_error: Specific exception error message (sanitized)
        message: Additional message or success message
        status_code: HTTP status code

    Returns:
        JSONResponse with standardized envelope
    """
    response_data = StandardResponse(
        success=success,
        data=data,
        error=error,
        exceptionError=exception_error,
        message=message
    )

    return JSONResponse(
        content=response_data.model_dump(exclude_none=True),
        status_code=status_code
    )
