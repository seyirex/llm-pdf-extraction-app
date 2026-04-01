"""Unit tests for validation service — checks and auto-corrections."""

import pytest

from src.schemas.extraction import ExtractedData, ExtractedHeader, ExtractedPosition
from src.services.validation_service import validate


class TestDateValidation:
    """Tests for date format validation."""

    def test_valid_date_format(self, sample_extracted_data_file1) -> None:
        result = validate(sample_extracted_data_file1)
        date_warnings = [w for w in result.warnings if "date format" in w.lower()]
        assert len(date_warnings) == 0

    def test_invalid_date_format(self, sample_extracted_data_file1) -> None:
        data = sample_extracted_data_file1.model_dump()
        data["header"]["liefertermin"] = "2026-05-15"
        extracted = ExtractedData.model_validate(data)
        result = validate(extracted)
        date_warnings = [w for w in result.warnings if "date format" in w.lower()]
        assert len(date_warnings) == 1


class TestGesamtValidation:
    """Tests for Gesamt vs Stück sum check."""

    def test_gesamt_matches(self, sample_extracted_data_file1) -> None:
        result = validate(sample_extracted_data_file1)
        gesamt_warnings = [w for w in result.warnings if "Gesamt mismatch" in w]
        assert len(gesamt_warnings) == 0

    def test_gesamt_mismatch(self, sample_extracted_data_file1) -> None:
        data = sample_extracted_data_file1.model_dump()
        data["header"]["gesamt"] = "99"
        extracted = ExtractedData.model_validate(data)
        result = validate(extracted)
        gesamt_warnings = [w for w in result.warnings if "Gesamt mismatch" in w]
        assert len(gesamt_warnings) == 1


class TestAutoCorrections:
    """Tests for automatic typo corrections."""

    def test_weift_to_weiss(self) -> None:
        """'Weift' should be auto-corrected to 'Weiß'."""
        data = ExtractedData(
            header=ExtractedHeader(
                lieferanschrift="Test GmbH",
                kommission="U2025-00001",
                rollladennummer="1234567890",
                liefertermin="01.01.2026",
                rollladen="Aluminium Weift",
                konstruktion="Standard",
                konstruktion_nummer="2960er",
                aussenschuerze="140 mm Hartschaum",
                endleiste="Aluminium-Abschlussleiste RAL 9006",
                antrieb="IO-homecontrol",
                gesamt="1",
            ),
            positions=[
                ExtractedPosition(
                    pos="EG1",
                    breite="1000",
                    hoehe="1000",
                    stueck="1",
                ),
            ],
        )
        result = validate(data)
        assert result.data.header.rollladen == "Aluminium Weiß"
        assert any("Weift" in c for c in result.corrections)

    def test_eicktro_to_elektro(self) -> None:
        """'Eicktro' should be auto-corrected to 'Elektro'."""
        data = ExtractedData(
            header=ExtractedHeader(
                lieferanschrift="Test GmbH",
                kommission="U2025-00001",
                rollladennummer="1234567890",
                liefertermin="01.01.2026",
                rollladen="Aluminium Silber",
                konstruktion="Standard",
                konstruktion_nummer="2960er",
                aussenschuerze="140 mm Hartschaum",
                endleiste="Aluminium-Abschlussleiste RAL 9006",
                antrieb="IO-homecontrol",
                gesamt="1",
            ),
            positions=[
                ExtractedPosition(
                    pos="EG1",
                    breite="1000",
                    hoehe="1000",
                    antrieb="Eicktro",
                    stueck="1",
                ),
            ],
        )
        result = validate(data)
        assert result.data.positions[0].antrieb == "Elektro"
        assert any("Eicktro" in c for c in result.corrections)

    def test_weibt_to_weiss(self) -> None:
        """'Weißt' should be auto-corrected to 'Weiß'."""
        data = ExtractedData(
            header=ExtractedHeader(
                lieferanschrift="Test GmbH",
                kommission="U2025-00001",
                rollladennummer="1234567890",
                liefertermin="01.01.2026",
                rollladen="Aluminium Weißt",
                konstruktion="Standard",
                konstruktion_nummer="2960er",
                aussenschuerze="140 mm Hartschaum",
                endleiste="Aluminium-Abschlussleiste RAL 9006",
                antrieb="IO-homecontrol",
                gesamt="1",
            ),
            positions=[
                ExtractedPosition(
                    pos="EG1",
                    breite="1000",
                    hoehe="1000",
                    stueck="1",
                ),
            ],
        )
        result = validate(data)
        assert result.data.header.rollladen == "Aluminium Weiß"
        assert any("Weißt" in c for c in result.corrections)
        assert not any("Unknown Rollladen" in w for w in result.warnings)

    def test_weibt_uppercase_variant_is_corrected(self) -> None:
        """Uppercase variant of 'Weißt' should also be auto-corrected."""
        data = ExtractedData(
            header=ExtractedHeader(
                lieferanschrift="Test GmbH",
                kommission="U2025-00001",
                rollladennummer="1234567890",
                liefertermin="01.01.2026",
                rollladen="Aluminium WEISST",
                konstruktion="Standard",
                konstruktion_nummer="2960er",
                aussenschuerze="140 mm Hartschaum",
                endleiste="Aluminium-Abschlussleiste RAL 9006",
                antrieb="IO-homecontrol",
                gesamt="1",
            ),
            positions=[
                ExtractedPosition(
                    pos="EG1",
                    breite="1000",
                    hoehe="1000",
                    stueck="1",
                ),
            ],
        )
        result = validate(data)
        assert result.data.header.rollladen == "Aluminium Weiß"
        assert not any("Unknown Rollladen" in w for w in result.warnings)


class TestUnknownValueWarnings:
    """Tests for warnings on unknown field values."""

    def test_unknown_rollladen(self) -> None:
        data = ExtractedData(
            header=ExtractedHeader(
                lieferanschrift="Test GmbH",
                kommission="U2025-00001",
                rollladennummer="1234567890",
                liefertermin="01.01.2026",
                rollladen="Kunststoff Blau",
                konstruktion="Standard",
                konstruktion_nummer="2960er",
                aussenschuerze="140 mm Hartschaum",
                endleiste="Aluminium-Abschlussleiste RAL 9006",
                antrieb="IO-homecontrol",
                gesamt="1",
            ),
            positions=[
                ExtractedPosition(
                    pos="EG1",
                    breite="1000",
                    hoehe="1000",
                    stueck="1",
                ),
            ],
        )
        result = validate(data)
        rollladen_warnings = [
            w for w in result.warnings if "Unknown Rollladen" in w
        ]
        assert len(rollladen_warnings) == 1

    def test_unknown_antrieb(self) -> None:
        data = ExtractedData(
            header=ExtractedHeader(
                lieferanschrift="Test GmbH",
                kommission="U2025-00001",
                rollladennummer="1234567890",
                liefertermin="01.01.2026",
                rollladen="Aluminium Silber",
                konstruktion="Standard",
                konstruktion_nummer="2960er",
                aussenschuerze="140 mm Hartschaum",
                endleiste="Aluminium-Abschlussleiste RAL 9006",
                antrieb="Manual Crank",
                gesamt="1",
            ),
            positions=[
                ExtractedPosition(
                    pos="EG1",
                    breite="1000",
                    hoehe="1000",
                    stueck="1",
                ),
            ],
        )
        result = validate(data)
        antrieb_warnings = [
            w for w in result.warnings if "Unknown Antrieb" in w
        ]
        assert len(antrieb_warnings) == 1
