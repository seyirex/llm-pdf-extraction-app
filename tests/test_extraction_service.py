"""Unit tests for extraction service — prompt construction and JSON parsing."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.schemas.extraction import ExtractedData
from src.services.extraction_service import ExtractionService


class TestExtractionService:
    """Tests for the extraction service with mocked Gemini client."""

    def test_extract_parses_valid_json(
        self, mock_gemini_client, sample_extracted_header_file1,
        sample_positions_file1, tmp_path
    ) -> None:
        """Valid JSON from Gemini should parse into ExtractedData."""
        response_data = {
            "header": sample_extracted_header_file1,
            "positions": sample_positions_file1,
        }
        mock_gemini_client.generate_json.return_value = json.dumps(
            response_data
        )

        service = ExtractionService(gemini_client=mock_gemini_client)
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 test")

        result = service.extract(pdf_path)
        assert isinstance(result, ExtractedData)
        assert result.header.lieferanschrift == "Musterbau & Holztechnik GmbH"
        assert len(result.positions) == 3

    def test_extract_raises_on_invalid_json(
        self, mock_gemini_client, tmp_path
    ) -> None:
        """Invalid JSON from Gemini should raise ValueError."""
        mock_gemini_client.generate_json.return_value = "not valid json"

        service = ExtractionService(gemini_client=mock_gemini_client)
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 test")

        with pytest.raises(ValueError, match="Invalid JSON"):
            service.extract(pdf_path)

    def test_extract_raises_on_missing_fields(
        self, mock_gemini_client, tmp_path
    ) -> None:
        """JSON missing required fields should raise ValueError."""
        mock_gemini_client.generate_json.return_value = json.dumps(
            {"header": {}, "positions": []}
        )

        service = ExtractionService(gemini_client=mock_gemini_client)
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 test")

        with pytest.raises(ValueError, match="validation failed"):
            service.extract(pdf_path)

    def test_extract_calls_gemini_with_pdf(
        self, mock_gemini_client, sample_extracted_header_file1,
        sample_positions_file1, tmp_path
    ) -> None:
        """Extraction should upload PDF and call generate_json."""
        response_data = {
            "header": sample_extracted_header_file1,
            "positions": sample_positions_file1,
        }
        mock_gemini_client.generate_json.return_value = json.dumps(
            response_data
        )

        service = ExtractionService(gemini_client=mock_gemini_client)
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 test")

        service.extract(pdf_path)
        mock_gemini_client.upload_pdf.assert_called_once_with(pdf_path)
        mock_gemini_client.generate_json.assert_called_once()
