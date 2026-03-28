"""Unit tests for TXT generator service — output format validation."""

import pytest

from src.services.mapping_service import apply_mapping_rules
from src.services.txt_generator_service import generate_txt_content, generate_txt_file


class TestGenerateTxtContent:
    """Tests for TXT content generation."""

    def test_header_row_has_11_columns(self, sample_extracted_data_file1) -> None:
        """Header row must have exactly 11 tab-separated columns."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        content = generate_txt_content(mapped)
        lines = content.split("\n")
        header_columns = lines[0].split("\t")
        assert len(header_columns) == 11

    def test_position_rows_have_10_columns(
        self, sample_extracted_data_file1
    ) -> None:
        """Each position row must have exactly 10 tab-separated columns."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        content = generate_txt_content(mapped)
        lines = content.split("\n")
        for pos_line in lines[1:]:
            pos_columns = pos_line.split("\t")
            assert len(pos_columns) == 10

    def test_correct_number_of_lines(
        self, sample_extracted_data_file1
    ) -> None:
        """Output should have 1 header + N position lines."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        content = generate_txt_content(mapped)
        lines = content.split("\n")
        # 1 header + 3 positions
        assert len(lines) == 4

    def test_tab_separation(self, sample_extracted_data_file1) -> None:
        """All columns must be separated by tabs, not spaces."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        content = generate_txt_content(mapped)
        assert "\t" in content

    def test_header_values_correct(self, sample_extracted_data_file1) -> None:
        """Verify specific mapped header values appear in output."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        content = generate_txt_content(mapped)
        header_line = content.split("\n")[0]
        assert "SILBER" in header_line
        assert "hwf9006" in header_line
        assert "IO" in header_line


class TestGenerateTxtFile:
    """Tests for TXT file writing."""

    def test_file_created(
        self, sample_extracted_data_file1, tmp_output_dir
    ) -> None:
        """Generated TXT file should exist on disk."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        output_path = tmp_output_dir / "test_output.txt"
        result_path = generate_txt_file(mapped, output_path)
        assert result_path.exists()

    def test_file_encoding_utf8(
        self, sample_extracted_data_file1, tmp_output_dir
    ) -> None:
        """Generated file should be readable as UTF-8."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        output_path = tmp_output_dir / "test_output.txt"
        generate_txt_file(mapped, output_path)
        content = output_path.read_text(encoding="utf-8")
        assert len(content) > 0
