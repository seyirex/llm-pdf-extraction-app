"""Centralized application exceptions."""


class AppException(Exception):
    """Application-level exception with HTTP status and machine-readable error code."""

    TASK_NOT_FOUND = "task_not_found"
    TASK_NOT_COMPLETE = "task_not_complete"
    TASK_FAILED = "task_failed"
    FILE_NOT_FOUND = "file_not_found"
    BAD_REQUEST = "bad_request"
    PAYLOAD_TOO_LARGE = "payload_too_large"
    EXTRACTION_FAILED = "extraction_failed"
    VALIDATION_ERROR = "validation_error"

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "internal_error",
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
