"""Unit tests for mapping service — all mapping rules in isolation."""

import pytest

from src.services.mapping_service import (
    apply_mapping_rules,
    map_antrieb_header,
    map_antrieb_position,
    map_bemerkung,
    map_bemerkung_nummer,
    map_endleiste,
    map_links,
    map_rechts,
    map_rollladen,
)


class TestMapRollladen:
    """Tests for Rollladen material mapping."""

    def test_aluminium_silber(self) -> None:
        assert map_rollladen("Aluminium Silber") == "SILBER"

    def test_aluminium_anthrazit(self) -> None:
        assert map_rollladen("Aluminium Anthrazit") == "ANTHRAZIT"

    def test_aluminium_weiss(self) -> None:
        assert map_rollladen("Aluminium Weiß") == "WEISS"

    def test_case_insensitive(self) -> None:
        assert map_rollladen("aluminium silber") == "SILBER"

    def test_weiss_alternate_spelling(self) -> None:
        assert map_rollladen("Aluminium Weiss") == "WEISS"

    def test_unknown_returns_raw(self) -> None:
        assert map_rollladen("Kunststoff Blau") == "Kunststoff Blau"


class TestMapEndleiste:
    """Tests for Endleiste code mapping."""

    def test_ral_9006(self) -> None:
        assert map_endleiste("Aluminium-Abschlussleiste RAL 9006") == "hwf9006"

    def test_ral_7016(self) -> None:
        assert map_endleiste("Aluminium-Abschlussleiste RAL 7016") == "hwf7016"

    def test_ral_9016(self) -> None:
        assert map_endleiste("Aluminium-Abschlussleiste RAL 9016") == "hwf9016"

    def test_unknown_returns_raw(self) -> None:
        raw = "Aluminium-Abschlussleiste RAL 1234"
        assert map_endleiste(raw) == raw


class TestMapAntriebHeader:
    """Tests for header Antrieb mapping."""

    def test_io_homecontrol(self) -> None:
        assert map_antrieb_header("IO-homecontrol") == "IO"

    def test_smi(self) -> None:
        assert map_antrieb_header("SMI") == "SMI"

    def test_smi_with_description(self) -> None:
        assert map_antrieb_header("SMI Motor") == "SMI"

    def test_unknown_returns_raw(self) -> None:
        assert map_antrieb_header("Manual") == "Manual"


class TestMapLinks:
    """Tests for L column binary mapping."""

    def test_l_present(self) -> None:
        assert map_links("L") == "1"

    def test_empty(self) -> None:
        assert map_links("") == "0"

    def test_lowercase(self) -> None:
        assert map_links("l") == "1"


class TestMapRechts:
    """Tests for R column binary mapping."""

    def test_r_present(self) -> None:
        assert map_rechts("R") == "1"

    def test_empty(self) -> None:
        assert map_rechts("") == "0"

    def test_lowercase(self) -> None:
        assert map_rechts("r") == "1"


class TestMapAntriebPosition:
    """Tests for position Antrieb mapping."""

    def test_elektro_with_io(self) -> None:
        assert map_antrieb_position("Elektro", "IO") == "1"

    def test_elektro_with_smi(self) -> None:
        assert map_antrieb_position("Elektro", "SMI") == "2"

    def test_empty_antrieb(self) -> None:
        assert map_antrieb_position("", "IO") == "0"

    def test_non_elektro(self) -> None:
        assert map_antrieb_position("Manual", "IO") == "0"


class TestMapBemerkung:
    """Tests for Bemerkung mapping."""

    def test_notkurbel(self) -> None:
        assert map_bemerkung("Notkurbel") == "8"

    def test_rolladenkasten(self) -> None:
        assert map_bemerkung("Rolladenkasten 180 mm") == "Rolladenkasten"

    def test_empty(self) -> None:
        assert map_bemerkung("") == "0"

    def test_other_text(self) -> None:
        assert map_bemerkung("Sonderwunsch") == "0"


class TestMapBemerkungNummer:
    """Tests for Bemerkung dimension extraction."""

    def test_180mm(self) -> None:
        assert map_bemerkung_nummer("Rolladenkasten 180 mm") == "180mm"

    def test_200mm_no_space(self) -> None:
        assert map_bemerkung_nummer("Rolladenkasten 200mm") == "200mm"

    def test_no_dimension(self) -> None:
        assert map_bemerkung_nummer("Notkurbel") == "0"

    def test_empty(self) -> None:
        assert map_bemerkung_nummer("") == "0"


class TestApplyMappingRules:
    """Tests for full mapping pipeline."""

    def test_full_mapping_file1(self, sample_extracted_data_file1) -> None:
        """Verify complete mapping for FILE 1 fixture data."""
        result = apply_mapping_rules(sample_extracted_data_file1)

        assert result.header.rollladen == "SILBER"
        assert result.header.endleiste == "hwf9006"
        assert result.header.antrieb == "IO"

        assert len(result.positions) == 3
        assert result.positions[0].line == 1
        assert result.positions[0].links == "1"
        assert result.positions[0].rechts == "0"
        assert result.positions[0].antrieb == "1"
        assert result.positions[0].bemerkung == "8"
        assert result.positions[0].pos == "EG1"

        assert result.positions[2].bemerkung == "Rolladenkasten"
        assert result.positions[2].bemerkung_nummer == "180mm"

    def test_full_mapping_file2(self, sample_extracted_data_file2) -> None:
        """Verify complete mapping for FILE 2 fixture data."""
        result = apply_mapping_rules(sample_extracted_data_file2)

        assert result.header.rollladen == "ANTHRAZIT"
        assert result.header.endleiste == "hwf7016"
        assert result.header.antrieb == "SMI"

        assert len(result.positions) == 2
        assert result.positions[0].antrieb == "2"
        assert result.positions[1].antrieb == "0"
        assert result.positions[1].bemerkung == "8"
