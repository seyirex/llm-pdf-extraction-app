"""Auth configuration endpoint for frontend clients."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.config import settings
from src.utils.responses import generate_response

router = APIRouter()


@router.get(
    "/auth/config",
    status_code=status.HTTP_200_OK,
    summary="Get auth configuration",
    description="Returns whether API key auth is enabled for this deployment.",
)
def get_auth_config() -> JSONResponse:
    """Return public auth configuration used by the frontend."""
    return generate_response(
        success=True,
        data={
            "enabled": settings.api_key_auth_enabled,
            "header_name": settings.api_key_header_name,
        },
        status_code=status.HTTP_200_OK,
    )
