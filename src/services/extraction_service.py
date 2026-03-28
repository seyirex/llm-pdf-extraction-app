"""Extraction service — calls Gemini with the prompt and parses JSON."""

import json
from pathlib import Path

from src.core.prompt import EXTRACTION_PROMPT
from src.schemas.extraction import ExtractedData
from src.utils.logger import get_logger

logger = get_logger()
from src.services.gemini_client import GeminiClient


class ExtractionService:
    """Handles PDF data extraction via the Gemini API.

    Builds the extraction prompt, sends it to Gemini with the PDF,
    and parses the JSON response into validated Pydantic models.
    """

    def __init__(self, gemini_client: GeminiClient | None = None) -> None:
        """Initialize the extraction service.

        Args:
            gemini_client: Optional GeminiClient instance for dependency injection.
        """
        self._client = gemini_client or GeminiClient()

    def extract(self, pdf_path: Path) -> ExtractedData:
        """Extract structured data from a PDF file.

        Args:
            pdf_path: Path to the PDF file to process.

        Returns:
            Validated ExtractedData with header and positions.

        Raises:
            ValueError: If the PDF cannot be processed or JSON is invalid.
        """
        uploaded_file = self._client.upload_pdf(pdf_path)
        raw_json = self._client.generate_json(EXTRACTION_PROMPT, uploaded_file)

        logger.debug(f"Raw Gemini response: {raw_json[:500]}")

        try:
            data_dict = json.loads(raw_json)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            raise ValueError(f"Invalid JSON from Gemini: {e}") from e

        try:
            extracted = ExtractedData.model_validate(data_dict)
        except Exception as e:
            logger.error(f"Failed to validate extracted data: {e}")
            raise ValueError(f"Extracted data validation failed: {e}") from e

        logger.info(
            f"Extraction complete: {len(extracted.positions)} positions, "
            f"Gesamt={extracted.header.gesamt}"
        )
        return extracted
