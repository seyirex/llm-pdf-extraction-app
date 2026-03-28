"""Mapping service — deterministic Python rules for field transformation."""

from src.schemas.extraction import ExtractedData
from src.schemas.mapping import MappedHeader, MappedPosition, MappedResult
from src.utils.constants import BEMERKUNG_MM_PATTERN
from src.utils.logger import get_logger

logger = get_logger()


def map_rollladen(raw_value: str) -> str:
    """Map Rollladen material description to output code.

    Args:
        raw_value: Raw Rollladen text (e.g., 'Aluminium Silber').

    Returns:
        Mapped code: SILBER, ANTHRAZIT, or WEISS.
    """
    value_lower = raw_value.lower()
    if "silber" in value_lower:
        return "SILBER"
    if "anthrazit" in value_lower:
        return "ANTHRAZIT"
    if "weiß" in value_lower or "weiss" in value_lower:
        return "WEISS"
    logger.warning(f"Unknown Rollladen value, returning raw: '{raw_value}'")
    return raw_value


def map_endleiste(raw_value: str) -> str:
    """Map Endleiste description to output code.

    Args:
        raw_value: Raw Endleiste text with RAL code.

    Returns:
        Mapped code: hwf9006, hwf7016, or hwf9016.
    """
    if raw_value.endswith("9006"):
        return "hwf9006"
    if raw_value.endswith("7016"):
        return "hwf7016"
    if raw_value.endswith("9016"):
        return "hwf9016"
    logger.warning(f"Unknown Endleiste value, returning raw: '{raw_value}'")
    return raw_value


def map_antrieb_header(raw_value: str) -> str:
    """Map header Antrieb description to output code.

    Args:
        raw_value: Raw Antrieb text from header (e.g., 'IO-homecontrol').

    Returns:
        Mapped code: SMI or IO.
    """
    value_upper = raw_value.upper()
    if "SMI" in value_upper:
        return "SMI"
    if "IO" in value_upper:
        return "IO"
    logger.warning(
        f"Unknown header Antrieb value, returning raw: '{raw_value}'"
    )
    return raw_value


def map_links(raw_value: str) -> str:
    """Map L column to binary flag.

    Args:
        raw_value: Raw L column value.

    Returns:
        '1' if L is present, '0' otherwise.
    """
    return "1" if "L" in raw_value.upper() else "0"


def map_rechts(raw_value: str) -> str:
    """Map R column to binary flag.

    Args:
        raw_value: Raw R column value.

    Returns:
        '1' if R is present, '0' otherwise.
    """
    return "1" if "R" in raw_value.upper() else "0"


def map_antrieb_position(
    position_antrieb: str, header_antrieb_mapped: str
) -> str:
    """Map position Antrieb based on position value and header drive type.

    Args:
        position_antrieb: Antrieb value from the position row.
        header_antrieb_mapped: Already-mapped header Antrieb (IO or SMI).

    Returns:
        '1' if Elektro + IO, '2' if Elektro + SMI, '0' otherwise.
    """
    if "elektro" in position_antrieb.lower():
        if header_antrieb_mapped == "IO":
            return "1"
        if header_antrieb_mapped == "SMI":
            return "2"
    return "0"


def map_bemerkung(raw_value: str) -> str:
    """Map Bemerkung text to output code.

    Args:
        raw_value: Raw Bemerkung text from position row.

    Returns:
        '8' if Notkurbel, 'Rolladenkasten' if present, '0' otherwise.
    """
    value_lower = raw_value.lower()
    if "notkurbel" in value_lower:
        return "8"
    if "rolladenkasten" in value_lower:
        return "Rolladenkasten"
    return "0"


def map_bemerkung_nummer(raw_value: str) -> str:
    """Extract dimension number from Bemerkung text.

    Args:
        raw_value: Raw Bemerkung text (e.g., 'Rolladenkasten 180 mm').

    Returns:
        Dimension string (e.g., '180mm') or '0' if no dimension found.
    """
    match = BEMERKUNG_MM_PATTERN.search(raw_value)
    if match:
        return f"{match.group(1)}mm"
    return "0"


def apply_mapping_rules(extracted: ExtractedData) -> MappedResult:
    """Apply all mapping rules to extracted data.

    Args:
        extracted: Validated extracted data from the PDF.

    Returns:
        MappedResult with header and positions transformed by mapping rules.
    """
    header = extracted.header
    header_antrieb_mapped = map_antrieb_header(header.antrieb)

    mapped_header = MappedHeader(
        lieferanschrift=header.lieferanschrift,
        kommission=header.kommission,
        rollladennummer=header.rollladennummer,
        liefertermin=header.liefertermin,
        rollladen=map_rollladen(header.rollladen),
        konstruktion=header.konstruktion,
        konstruktion_nummer=header.konstruktion_nummer,
        aussenschuerze=header.aussenschuerze,
        endleiste=map_endleiste(header.endleiste),
        antrieb=header_antrieb_mapped,
        gesamt=header.gesamt,
    )

    mapped_positions: list[MappedPosition] = []
    for idx, position in enumerate(extracted.positions, start=1):
        mapped_position = MappedPosition(
            line=idx,
            stueck=position.stueck,
            breite=position.breite,
            hoehe=position.hoehe,
            links=map_links(position.links),
            rechts=map_rechts(position.rechts),
            antrieb=map_antrieb_position(
                position.antrieb, header_antrieb_mapped
            ),
            pos=position.pos,
            bemerkung=map_bemerkung(position.bemerkung),
            bemerkung_nummer=map_bemerkung_nummer(position.bemerkung),
        )
        mapped_positions.append(mapped_position)

    logger.info(
        f"Mapping complete: {len(mapped_positions)} positions mapped"
    )

    return MappedResult(
        header=mapped_header,
        positions=mapped_positions,
    )
