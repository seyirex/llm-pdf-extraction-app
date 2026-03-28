"""Pipeline service — orchestrates extraction, validation, mapping, and TXT generation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from src.schemas.extraction import ExtractedData
from src.utils.logger import get_logger

logger = get_logger()
from src.schemas.mapping import MappedResult
from src.services.extraction_service import ExtractionService
from src.services.mapping_service import apply_mapping_rules
from src.services.txt_generator_service import generate_txt_file
from src.services.validation_service import ValidationResult, validate


@dataclass
class PipelineResult:
    """Complete result from the PDF processing pipeline.

    Attributes:
        extracted: Raw extracted data from Gemini.
        validation: Validation result with corrections and warnings.
        mapped: Mapped data after applying transformation rules.
        txt_path: Path to the generated TXT output file.
    """

    extracted: ExtractedData
    validation: ValidationResult
    mapped: MappedResult
    txt_path: Path
    warnings: list[str] = field(default_factory=list)
    corrections: list[str] = field(default_factory=list)


def run_pipeline(
    pdf_path: Path,
    output_path: Path,
    extraction_service: ExtractionService | None = None,
    on_progress: Callable[[str], None] | None = None,
) -> PipelineResult:
    """Run the full PDF processing pipeline.

    Pipeline steps: extract → validate → map → generate TXT.
    If a Gesamt mismatch is detected, retries extraction once.

    Args:
        pdf_path: Path to the uploaded PDF file.
        output_path: Path for the generated TXT output file.
        extraction_service: Optional ExtractionService for dependency injection.
        on_progress: Optional callback for progress updates, receives step name.

    Returns:
        PipelineResult with all intermediate and final data.

    Raises:
        ValueError: If extraction or validation fails critically.
    """
    service = extraction_service or ExtractionService()

    # Step 1: Extract
    if on_progress:
        on_progress("extracting")
    logger.info(f"Pipeline step 1/4: Extracting data from {pdf_path.name}")
    extracted = service.extract(pdf_path)

    # Step 2: Validate
    if on_progress:
        on_progress("validating")
    logger.info("Pipeline step 2/4: Validating extracted data")
    validation = validate(extracted)

    # Retry extraction once if Gesamt mismatch or unknown Rollladen detected
    retry_warnings = [
        w for w in validation.warnings
        if "Gesamt mismatch" in w or "Unknown Rollladen" in w
    ]
    if retry_warnings:
        logger.warning(f"Validation issues detected — retrying extraction: {retry_warnings}")
        if on_progress:
            on_progress("retrying_extraction")
        extracted = service.extract(pdf_path)
        validation = validate(extracted)

    # Step 3: Map
    if on_progress:
        on_progress("mapping")
    logger.info("Pipeline step 3/4: Applying mapping rules")
    mapped = apply_mapping_rules(validation.data)

    # Step 4: Generate TXT
    if on_progress:
        on_progress("generating")
    logger.info("Pipeline step 4/4: Generating TXT output")
    txt_path = generate_txt_file(mapped, output_path)

    logger.info(f"Pipeline complete: {txt_path}")
    return PipelineResult(
        extracted=extracted,
        validation=validation,
        mapped=mapped,
        txt_path=txt_path,
        warnings=validation.warnings,
        corrections=validation.corrections,
    )
