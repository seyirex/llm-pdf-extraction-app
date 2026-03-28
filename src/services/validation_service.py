"""Validation service — auto-corrections and domain checks on extracted data."""

from dataclasses import dataclass, field

from src.schemas.extraction import ExtractedData
from src.utils.constants import (
    DATE_PATTERN,
    ENDLEISTE_PATTERN,
    KNOWN_ANTRIEB_KEYWORDS,
    KNOWN_ROLLLADEN_VALUES,
    TYPO_CORRECTIONS,
)
from src.utils.logger import get_logger

logger = get_logger()


@dataclass
class ValidationResult:
    """Result of validation with corrected data and warnings.

    Attributes:
        data: The corrected ExtractedData.
        warnings: List of warning messages from validation checks.
        corrections: List of auto-corrections that were applied.
    """

    data: ExtractedData
    warnings: list[str] = field(default_factory=list)
    corrections: list[str] = field(default_factory=list)


def _apply_typo_corrections(text: str) -> tuple[str, list[str]]:
    """Apply known typo corrections to a text value.

    Args:
        text: The text to check for typos.

    Returns:
        Tuple of corrected text and list of correction descriptions.
    """
    corrections_applied: list[str] = []
    corrected = text
    for typo, fix in TYPO_CORRECTIONS.items():
        if typo in corrected:
            corrected = corrected.replace(typo, fix)
            corrections_applied.append(f"'{typo}' → '{fix}'")
    return corrected, corrections_applied


def validate(extracted: ExtractedData) -> ValidationResult:
    """Validate and auto-correct extracted PDF data.

    Applies typo corrections, checks date formats, validates
    Gesamt vs sum of Stück, and warns about unknown field values.

    Args:
        extracted: Raw extracted data from Gemini.

    Returns:
        ValidationResult with corrected data and any warnings.
    """
    warnings: list[str] = []
    corrections: list[str] = []

    data_dict = extracted.model_dump()
    header = data_dict["header"]

    # Auto-correct Rollladen typos
    corrected_rollladen, rollladen_corrections = _apply_typo_corrections(
        header["rollladen"]
    )
    header["rollladen"] = corrected_rollladen
    corrections.extend(rollladen_corrections)

    # Auto-correct position Antrieb typos
    for position in data_dict["positions"]:
        corrected_antrieb, antrieb_corrections = _apply_typo_corrections(
            position["antrieb"]
        )
        position["antrieb"] = corrected_antrieb
        corrections.extend(antrieb_corrections)

        # Auto-correct Bemerkung typos
        corrected_bemerkung, bemerkung_corrections = _apply_typo_corrections(
            position["bemerkung"]
        )
        position["bemerkung"] = corrected_bemerkung
        corrections.extend(bemerkung_corrections)

    # Validate date format
    if not DATE_PATTERN.match(header["liefertermin"]):
        warnings.append(
            f"Invalid date format: '{header['liefertermin']}' "
            f"(expected DD.MM.YYYY)"
        )

    # Validate Gesamt vs sum of Stück
    try:
        gesamt = int(header["gesamt"])
        stueck_sum = sum(int(p["stueck"]) for p in data_dict["positions"])
        if gesamt != stueck_sum:
            warnings.append(
                f"Gesamt mismatch: header says {gesamt}, "
                f"sum of Stück is {stueck_sum}"
            )
    except ValueError:
        warnings.append(
            f"Non-numeric Gesamt or Stück values detected"
        )

    # Warn about unknown Rollladen values
    if header["rollladen"] not in KNOWN_ROLLLADEN_VALUES:
        warnings.append(
            f"Unknown Rollladen value: '{header['rollladen']}'"
        )

    # Warn about unknown Antrieb values
    antrieb_known = any(
        keyword in header["antrieb"] for keyword in KNOWN_ANTRIEB_KEYWORDS
    )
    if not antrieb_known:
        warnings.append(
            f"Unknown Antrieb value: '{header['antrieb']}'"
        )

    # Warn about unknown Endleiste values
    if not ENDLEISTE_PATTERN.search(header["endleiste"]):
        warnings.append(
            f"Unknown Endleiste value: '{header['endleiste']}'"
        )

    corrected_data = ExtractedData.model_validate(data_dict)

    if corrections:
        logger.info(f"Auto-corrections applied: {corrections}")
    if warnings:
        logger.warning(f"Validation warnings: {warnings}")

    return ValidationResult(
        data=corrected_data,
        warnings=warnings,
        corrections=corrections,
    )
