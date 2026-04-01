"""API tests — upload, status, result, download endpoints."""

import io
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api.dependencies import get_task_service
from src.config import settings
from src.main import app
from src.services.task_service import TaskResult, TaskStatus
from src.utils.exceptions import AppException


@pytest.fixture(autouse=True)
def disable_api_key_auth_by_default(monkeypatch):
    """Keep tests independent from local .env auth settings."""
    monkeypatch.setattr(settings, "api_key_auth_enabled", False)
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "api_key_header_name", "x-api-key")


@pytest.fixture
def mock_task_service():
    """Mock TaskService injected via dependency override."""
    mock = MagicMock()
    app.dependency_overrides[get_task_service] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


@pytest.fixture
def client(mock_task_service):
    """FastAPI TestClient fixture with dependency overrides applied."""
    return TestClient(app)


class TestUploadEndpoint:
    """Tests for POST /api/v1/upload."""

    def test_upload_valid_pdf(self, mock_task_service, client) -> None:
        """Valid PDF upload should return 202 with task_id."""
        mock_task_service.save_and_dispatch.return_value = "test-task-id"

        pdf_content = b"%PDF-1.4 test content"
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")},
        )

        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert data["data"]["task_id"] == "test-task-id"
        assert data["message"] == "PDF uploaded and processing started"

    def test_upload_non_pdf_rejected(self, client) -> None:
        """Non-PDF file should be rejected with 400."""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.txt", io.BytesIO(b"text"), "text/plain")},
        )
        assert response.status_code == 400

    def test_upload_no_file(self, client) -> None:
        """Missing file should return 422."""
        response = client.post("/api/v1/upload")
        assert response.status_code == 422


class TestStatusEndpoint:
    """Tests for GET /api/v1/status/{task_id}."""

    def test_status_pending(self, mock_task_service, client) -> None:
        """Pending task should return PENDING status."""
        mock_task_service.get_status.return_value = TaskStatus(
            task_id="test-task-id", state="PENDING", step=None,
        )

        response = client.get("/api/v1/status/test-task-id")
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "PENDING"

    def test_status_progress(self, mock_task_service, client) -> None:
        """In-progress task should return step info."""
        mock_task_service.get_status.return_value = TaskStatus(
            task_id="test-task-id", state="PROGRESS", step="mapping",
        )

        response = client.get("/api/v1/status/test-task-id")
        data = response.json()
        assert data["data"]["status"] == "PROGRESS"
        assert data["data"]["step"] == "mapping"


class TestResultEndpoint:
    """Tests for GET /api/v1/result/{task_id}."""

    def test_result_success(self, mock_task_service, client) -> None:
        """Completed task should return full results."""
        mock_task_service.get_result.return_value = TaskResult(
            task_id="test-task-id",
            extracted={"header": {}, "positions": []},
            mapped={"header": {}, "positions": []},
            warnings=[],
            corrections=[],
        )

        response = client.get("/api/v1/result/test-task-id")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "extracted" in data["data"]
        assert "mapped" in data["data"]

    def test_result_not_complete(self, mock_task_service, client) -> None:
        """Non-complete task should return 409."""
        mock_task_service.get_result.side_effect = AppException(
            message="Task not yet complete",
            status_code=409,
            error_code=AppException.TASK_NOT_COMPLETE,
        )

        response = client.get("/api/v1/result/test-task-id")
        assert response.status_code == 409

    def test_result_not_found(self, mock_task_service, client) -> None:
        """Pending/unknown task should return 404."""
        mock_task_service.get_result.side_effect = AppException(
            message="Task not found or still pending",
            status_code=404,
            error_code=AppException.TASK_NOT_FOUND,
        )

        response = client.get("/api/v1/result/test-task-id")
        assert response.status_code == 404

    def test_result_failed(self, mock_task_service, client) -> None:
        """Failed task should return 500."""
        mock_task_service.get_result.side_effect = AppException(
            message="Task failed: some error",
            status_code=500,
            error_code=AppException.TASK_FAILED,
        )

        response = client.get("/api/v1/result/test-task-id")
        assert response.status_code == 500


class TestDownloadEndpoint:
    """Tests for GET /api/v1/download/{task_id}."""

    def test_download_success(self, mock_task_service, client, tmp_path) -> None:
        """Completed task with file should return TXT download."""
        txt_file = tmp_path / "test_output.txt"
        txt_file.write_text("col1\tcol2\n", encoding="utf-8")

        mock_task_service.get_download_path.return_value = txt_file

        response = client.get("/api/v1/download/test-task-id")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    def test_download_not_ready(self, mock_task_service, client) -> None:
        """Non-complete task should return 409."""
        mock_task_service.get_download_path.side_effect = AppException(
            message="Task not yet complete",
            status_code=409,
            error_code=AppException.TASK_NOT_COMPLETE,
        )

        response = client.get("/api/v1/download/test-task-id")
        assert response.status_code == 409

    def test_download_file_missing(self, mock_task_service, client) -> None:
        """Missing output file should return 404."""
        mock_task_service.get_download_path.side_effect = AppException(
            message="Generated TXT file not found",
            status_code=404,
            error_code=AppException.FILE_NOT_FOUND,
        )

        response = client.get("/api/v1/download/test-task-id")
        assert response.status_code == 404


class TestPdfEndpoint:
    """Tests for GET /api/v1/pdf/{task_id}."""

    def test_pdf_preview_success(self, mock_task_service, client, tmp_path) -> None:
        """Existing PDF should be returned with correct content type."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test content")

        mock_task_service.get_pdf_path.return_value = pdf_file

        response = client.get("/api/v1/pdf/test-task-id")
        assert response.status_code == 200
        assert "application/pdf" in response.headers["content-type"]

    def test_pdf_preview_not_found(self, mock_task_service, client) -> None:
        """Pending/unknown task should return 404."""
        mock_task_service.get_pdf_path.side_effect = AppException(
            message="Task not found or still pending",
            status_code=404,
            error_code=AppException.TASK_NOT_FOUND,
        )

        response = client.get("/api/v1/pdf/test-task-id")
        assert response.status_code == 404

    def test_pdf_preview_file_missing(self, mock_task_service, client) -> None:
        """Missing PDF file on disk should return 404."""
        mock_task_service.get_pdf_path.side_effect = AppException(
            message="Uploaded PDF file not found",
            status_code=404,
            error_code=AppException.FILE_NOT_FOUND,
        )

        response = client.get("/api/v1/pdf/test-task-id")
        assert response.status_code == 404


class TestApiKeyAuth:
    """Tests for optional API key protection across API endpoints."""

    def test_auth_config_defaults_off(self, client) -> None:
        """Auth config endpoint should expose current toggle state."""
        response = client.get("/api/v1/auth/config")
        assert response.status_code == 200
        assert "enabled" in response.json()["data"]

    def test_status_requires_api_key_when_enabled(
        self, mock_task_service, client, monkeypatch
    ) -> None:
        """Protected endpoints should reject requests without key when enabled."""
        monkeypatch.setattr(settings, "api_key_auth_enabled", True)
        monkeypatch.setattr(settings, "api_key", "dev-key")
        monkeypatch.setattr(settings, "api_key_header_name", "x-api-key")

        response = client.get("/api/v1/status/test-task-id")
        assert response.status_code == 401

    def test_status_accepts_valid_api_key_when_enabled(
        self, mock_task_service, client, monkeypatch
    ) -> None:
        """Protected endpoints should pass with a valid API key."""
        monkeypatch.setattr(settings, "api_key_auth_enabled", True)
        monkeypatch.setattr(settings, "api_key", "dev-key")
        monkeypatch.setattr(settings, "api_key_header_name", "x-api-key")

        mock_task_service.get_status.return_value = TaskStatus(
            task_id="test-task-id", state="PENDING", step=None,
        )

        response = client.get(
            "/api/v1/status/test-task-id",
            headers={"x-api-key": "dev-key"},
        )
        assert response.status_code == 200
