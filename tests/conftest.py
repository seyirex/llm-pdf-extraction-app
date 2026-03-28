"""Shared test fixtures for PDF extraction tests."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from src.schemas.extraction import ExtractedData, ExtractedHeader, ExtractedPosition


@pytest.fixture
def sample_extracted_header_file1() -> dict:
    """Sample header data mimicking Gemini output for FILE 1."""
    return {
        "lieferanschrift": "Musterbau & Holztechnik GmbH",
        "kommission": "U2025-30770",
        "rollladennummer": "0702260411",
        "liefertermin": "15.05.2026",
        "rollladen": "Aluminium Silber",
        "konstruktion": "Erhöht",
        "konstruktion_nummer": "2960er",
        "aussenschuerze": "140 mm Hartschaum",
        "endleiste": "Aluminium-Abschlussleiste RAL 9006",
        "antrieb": "IO-homecontrol",
        "gesamt": "3",
    }


@pytest.fixture
def sample_positions_file1() -> list[dict]:
    """Sample positions data mimicking Gemini output for FILE 1."""
    return [
        {
            "pos": "EG1",
            "breite": "1200",
            "hoehe": "1500",
            "links": "L",
            "rechts": "",
            "antrieb": "Elektro",
            "bemerkung": "Notkurbel",
            "stueck": "1",
        },
        {
            "pos": "EG2",
            "breite": "1400",
            "hoehe": "1500",
            "links": "",
            "rechts": "R",
            "antrieb": "Elektro",
            "bemerkung": "",
            "stueck": "1",
        },
        {
            "pos": "DG1",
            "breite": "900",
            "hoehe": "1200",
            "links": "L",
            "rechts": "",
            "antrieb": "Elektro",
            "bemerkung": "Rolladenkasten 180 mm",
            "stueck": "1",
        },
    ]


@pytest.fixture
def sample_extracted_data_file1(
    sample_extracted_header_file1, sample_positions_file1
) -> ExtractedData:
    """Complete ExtractedData fixture for FILE 1."""
    return ExtractedData(
        header=ExtractedHeader(**sample_extracted_header_file1),
        positions=[
            ExtractedPosition(**p) for p in sample_positions_file1
        ],
    )


@pytest.fixture
def sample_extracted_header_file2() -> dict:
    """Sample header data mimicking Gemini output for FILE 2."""
    return {
        "lieferanschrift": "Beispielhaus GmbH",
        "kommission": "U2025-40123",
        "rollladennummer": "0803260512",
        "liefertermin": "20.06.2026",
        "rollladen": "Aluminium Anthrazit",
        "konstruktion": "Standard",
        "konstruktion_nummer": "2750er",
        "aussenschuerze": "120 mm Hartschaum",
        "endleiste": "Aluminium-Abschlussleiste RAL 7016",
        "antrieb": "SMI",
        "gesamt": "2",
    }


@pytest.fixture
def sample_positions_file2() -> list[dict]:
    """Sample positions data mimicking Gemini output for FILE 2."""
    return [
        {
            "pos": "EG1",
            "breite": "1100",
            "hoehe": "1400",
            "links": "",
            "rechts": "R",
            "antrieb": "Elektro",
            "bemerkung": "",
            "stueck": "1",
        },
        {
            "pos": "OG1",
            "breite": "1300",
            "hoehe": "1600",
            "links": "L",
            "rechts": "",
            "antrieb": "",
            "bemerkung": "Notkurbel",
            "stueck": "1",
        },
    ]


@pytest.fixture
def sample_extracted_data_file2(
    sample_extracted_header_file2, sample_positions_file2
) -> ExtractedData:
    """Complete ExtractedData fixture for FILE 2."""
    return ExtractedData(
        header=ExtractedHeader(**sample_extracted_header_file2),
        positions=[
            ExtractedPosition(**p) for p in sample_positions_file2
        ],
    )


@pytest.fixture
def mock_gemini_client():
    """Mock GeminiClient that returns fixture data."""
    client = MagicMock()
    client.upload_pdf.return_value = MagicMock(name="uploaded_file")
    return client


@pytest.fixture
def tmp_output_dir(tmp_path) -> Path:
    """Temporary directory for output files."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return output_dir
