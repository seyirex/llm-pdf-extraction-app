"""TXT generator service — builds tab-separated output files."""

from pathlib import Path

from src.schemas.mapping import MappedResult
from src.utils.constants import HEADER_COLUMNS, POSITION_COLUMNS
from src.utils.logger import get_logger

logger = get_logger()

POSITION_LABELS: dict[str, str] = {
    "links": "L",
    "rechts": "R",
}


def _sanitize_value(value: str) -> str:
    """Replace newlines and excess whitespace with a single space."""
    return " ".join(value.replace("\r", "").replace("\n", " ").split())


def generate_txt_content(mapped: MappedResult) -> str:
    """Generate tab-separated TXT content from mapped data.

    Produces a readable header section with one field per line,
    then a positions section with tab-separated columns.

    Args:
        mapped: The fully mapped result data.

    Returns:
        Text content for the output file.
    """
    header_dict = mapped.header.model_dump()
    key_width = max(len(col) for col in HEADER_COLUMNS)
    header_lines = [
        f"{col.ljust(key_width)} : {_sanitize_value(str(header_dict[col]))}"
        for col in HEADER_COLUMNS
    ]

    position_label_row = "\t".join(
        POSITION_LABELS.get(col, col) for col in POSITION_COLUMNS
    )
    position_rows: list[str] = []
    for position in mapped.positions:
        pos_dict = position.model_dump()
        pos_values = [_sanitize_value(str(pos_dict[col])) for col in POSITION_COLUMNS]
        position_rows.append("\t".join(pos_values))

    lines = ["HEADER"] + header_lines + ["", "POSITIONS", position_label_row] + position_rows
    return "\n".join(lines)


def generate_txt_file(mapped: MappedResult, output_path: Path) -> Path:
    """Generate a tab-separated TXT file from mapped data.

    Args:
        mapped: The fully mapped result data.
        output_path: Path where the TXT file should be written.

    Returns:
        Path to the generated TXT file.
    """
    content = generate_txt_content(mapped)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"TXT file generated: {output_path}")
    return output_path
