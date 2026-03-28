"""Integration tests for the pipeline service with mocked Gemini."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.services.extraction_service import ExtractionService
from src.services.pipeline_service import run_pipeline


class TestPipelineService:
    """Integration tests for the full processing pipeline."""

    def _make_mock_service(
        self, mock_gemini_client, header_data: dict, positions_data: list
    ) -> ExtractionService:
        """Create an ExtractionService with mocked Gemini responses.

        Args:
            mock_gemini_client: Mock Gemini client fixture.
            header_data: Header dict to return from Gemini.
            positions_data: Positions list to return from Gemini.

        Returns:
            ExtractionService configured with mock client.
        """
        response = json.dumps({
            "header": header_data,
            "positions": positions_data,
        })
        mock_gemini_client.generate_json.return_value = response
        return ExtractionService(gemini_client=mock_gemini_client)

    def test_pipeline_file1(
        self, mock_gemini_client, sample_extracted_header_file1,
        sample_positions_file1, tmp_path
    ) -> None:
        """Full pipeline produces correct TXT for FILE 1 data."""
        service = self._make_mock_service(
            mock_gemini_client,
            sample_extracted_header_file1,
            sample_positions_file1,
        )

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 test")
        output_path = tmp_path / "output.txt"

        result = run_pipeline(
            pdf_path=pdf_path,
            output_path=output_path,
            extraction_service=service,
        )

        assert result.txt_path.exists()
        content = result.txt_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # 1 header + 3 positions
        assert len(lines) == 4

        # Header checks
        header_cols = lines[0].split("\t")
        assert len(header_cols) == 11
        assert header_cols[4] == "SILBER"
        assert header_cols[8] == "hwf9006"
        assert header_cols[9] == "IO"

        # First position checks
        pos1_cols = lines[1].split("\t")
        assert len(pos1_cols) == 10
        assert pos1_cols[0] == "1"  # LINE
        assert pos1_cols[4] == "1"  # links=L → 1
        assert pos1_cols[5] == "0"  # rechts="" → 0
        assert pos1_cols[6] == "1"  # Elektro+IO → 1
        assert pos1_cols[8] == "8"  # Notkurbel → 8

    def test_pipeline_file2(
        self, mock_gemini_client, sample_extracted_header_file2,
        sample_positions_file2, tmp_path
    ) -> None:
        """Full pipeline produces correct TXT for FILE 2 data."""
        service = self._make_mock_service(
            mock_gemini_client,
            sample_extracted_header_file2,
            sample_positions_file2,
        )

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 test")
        output_path = tmp_path / "output.txt"

        result = run_pipeline(
            pdf_path=pdf_path,
            output_path=output_path,
            extraction_service=service,
        )

        content = result.txt_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        assert len(lines) == 3

        header_cols = lines[0].split("\t")
        assert header_cols[4] == "ANTHRAZIT"
        assert header_cols[8] == "hwf7016"
        assert header_cols[9] == "SMI"

        # Position 1: Elektro+SMI → 2
        pos1_cols = lines[1].split("\t")
        assert pos1_cols[6] == "2"

        # Position 2: no Elektro → 0
        pos2_cols = lines[2].split("\t")
        assert pos2_cols[6] == "0"
        assert pos2_cols[8] == "8"  # Notkurbel → 8

    def test_pipeline_calls_progress_callback(
        self, mock_gemini_client, sample_extracted_header_file1,
        sample_positions_file1, tmp_path
    ) -> None:
        """Pipeline should call progress callback at each step."""
        service = self._make_mock_service(
            mock_gemini_client,
            sample_extracted_header_file1,
            sample_positions_file1,
        )

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 test")
        output_path = tmp_path / "output.txt"

        progress_steps: list[str] = []
        run_pipeline(
            pdf_path=pdf_path,
            output_path=output_path,
            extraction_service=service,
            on_progress=lambda step: progress_steps.append(step),
        )

        assert "extracting" in progress_steps
        assert "validating" in progress_steps
        assert "mapping" in progress_steps
        assert "generating" in progress_steps
