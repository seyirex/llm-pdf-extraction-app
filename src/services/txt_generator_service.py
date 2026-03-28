"""TXT generator service — builds tab-separated output files."""

from pathlib import Path

from src.schemas.mapping import MappedResult
from src.utils.constants import HEADER_COLUMNS, POSITION_COLUMNS
from src.utils.logger import get_logger

logger = get_logger()


def generate_txt_content(mapped: MappedResult) -> str:
    """Generate tab-separated TXT content from mapped data.

    Produces a header row (11 columns) followed by one row per
    position (10 columns each), all tab-separated.

    Args:
        mapped: The fully mapped result data.

    Returns:
        Tab-separated string content for the output file.
    """
    header_dict = mapped.header.model_dump()
    header_values = [str(header_dict[col]) for col in HEADER_COLUMNS]
    header_row = "\t".join(header_values)

    position_rows: list[str] = []
    for position in mapped.positions:
        pos_dict = position.model_dump()
        pos_values = [str(pos_dict[col]) for col in POSITION_COLUMNS]
        position_rows.append("\t".join(pos_values))

    lines = [header_row] + position_rows
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
