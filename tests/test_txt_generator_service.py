"""Unit tests for TXT generator service — output format validation."""

from src.services.mapping_service import apply_mapping_rules
from src.services.txt_generator_service import generate_txt_content, generate_txt_file
from src.utils.constants import HEADER_COLUMNS, POSITION_COLUMNS


class TestGenerateTxtContent:
    """Tests for TXT content generation."""

    def test_header_section_has_all_fields(self, sample_extracted_data_file1) -> None:
        """Header section should include every expected header field."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        content = generate_txt_content(mapped)
        lines = content.split("\n")
        assert lines[0] == "HEADER"
        header_lines = lines[1 : 1 + len(HEADER_COLUMNS)]
        for field in HEADER_COLUMNS:
            assert any(line.startswith(field) for line in header_lines)

    def test_position_rows_have_10_columns(
        self, sample_extracted_data_file1
    ) -> None:
        """Each position row must have exactly 10 tab-separated columns."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        content = generate_txt_content(mapped)
        lines = content.split("\n")
        positions_idx = lines.index("POSITIONS")
        # Skip: positions section title (POSITIONS) and column labels
        for pos_line in lines[positions_idx + 2 :]:
            pos_columns = pos_line.split("\t")
            assert len(pos_columns) == len(POSITION_COLUMNS)

    def test_correct_number_of_lines(
        self, sample_extracted_data_file1
    ) -> None:
        """Output should include header section + positions section + all rows."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        content = generate_txt_content(mapped)
        lines = content.split("\n")
        expected_lines = 1 + len(HEADER_COLUMNS) + 1 + 1 + 1 + len(mapped.positions)
        assert len(lines) == expected_lines

    def test_tab_separation(self, sample_extracted_data_file1) -> None:
        """Position rows must remain tab-separated."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        content = generate_txt_content(mapped)
        positions_idx = content.split("\n").index("POSITIONS")
        position_header_line = content.split("\n")[positions_idx + 1]
        assert "\t" in position_header_line

    def test_header_values_correct(self, sample_extracted_data_file1) -> None:
        """Verify specific mapped header values appear in header section."""
        mapped = apply_mapping_rules(sample_extracted_data_file1)
        content = generate_txt_content(mapped)
        assert "SILBER" in content
        assert "hwf9006" in content
        assert "IO" in content


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
