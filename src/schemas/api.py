"""API request/response models."""

from pydantic import BaseModel, ConfigDict, Field


class UploadResponse(BaseModel):
    """Response returned after successful PDF upload.

    Attributes:
        task_id: Celery task ID for tracking processing status.
        message: Human-readable status message.
    """

    task_id: str = Field(
        ...,
        description="Celery task ID for polling processing status",
    )
    message: str = Field(
        ...,
        description="Human-readable status message",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "message": "PDF uploaded and processing started",
            }
        }
    )


class StatusResponse(BaseModel):
    """Response for task status polling.

    Attributes:
        task_id: Celery task ID.
        status: Current task status (PENDING, PROGRESS, SUCCESS, FAILURE).
        step: Current pipeline step if in progress.
    """

    task_id: str = Field(
        ...,
        description="Celery task ID",
    )
    status: str = Field(
        ...,
        description="Current task status (PENDING, PROGRESS, SUCCESS, FAILURE)",
    )
    step: str | None = Field(
        default=None,
        description="Current pipeline step if task is in progress",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "status": "PROGRESS",
                "step": "mapping",
            }
        }
    )


class ResultResponse(BaseModel):
    """Response containing full processing results.

    Attributes:
        task_id: Celery task ID.
        extracted: Raw extracted data from the PDF.
        mapped: Mapped data after applying rules.
        warnings: Validation warnings encountered.
        corrections: Auto-corrections applied during validation.
    """

    task_id: str = Field(
        ...,
        description="Celery task ID",
    )
    extracted: dict = Field(
        ...,
        description="Raw extracted data from the PDF",
    )
    mapped: dict = Field(
        ...,
        description="Mapped data after applying transformation rules",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Validation warnings encountered during processing",
    )
    corrections: list[str] = Field(
        default_factory=list,
        description="Auto-corrections applied during validation",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "extracted": {"header": {}, "positions": []},
                "mapped": {"header": {}, "positions": []},
                "warnings": ["Gesamt mismatch: header says 15, sum is 14"],
                "corrections": ["'Weift' -> 'Weiss'"],
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response.

    Attributes:
        detail: Error description.
    """

    detail: str = Field(
        ...,
        description="Error description",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "File must be a PDF",
            }
        }
    )
