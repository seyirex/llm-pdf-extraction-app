"""Gemini SDK wrapper for PDF upload and content generation."""

from pathlib import Path
from typing import Any

from google import genai
from google.genai import types
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger()


class GeminiClient:
    """Wrapper around Google Generative AI SDK for PDF extraction.

    Configures the SDK with the API key and provides methods
    for uploading PDFs and generating structured responses.
    """

    def __init__(self) -> None:
        """Initialize the Gemini client with API key configuration."""
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def upload_pdf(self, pdf_path: Path) -> Any:
        """Upload a PDF file to Gemini for processing.

        Args:
            pdf_path: Path to the PDF file to upload.

        Returns:
            Gemini file reference for use in generation calls.

        Raises:
            ValueError: If the file does not exist or is not a PDF.
        """
        if not pdf_path.exists():
            raise ValueError(f"PDF file not found: {pdf_path}")

        logger.info(f"Uploading PDF to Gemini: {pdf_path.name}")
        uploaded_file = self._client.files.upload(
            file=str(pdf_path),
            config=types.UploadFileConfig(mime_type="application/pdf"),
        )
        logger.info(f"PDF uploaded successfully: {uploaded_file.name}")
        return uploaded_file

    def generate_json(
        self, prompt: str, uploaded_file: Any
    ) -> str:
        """Generate a JSON response from Gemini using the uploaded PDF.

        Args:
            prompt: The extraction prompt to send to the model.
            uploaded_file: Gemini file reference from upload_pdf.

        Returns:
            Raw JSON string from the model response.
        """
        logger.info("Sending extraction request to Gemini")
        response = self._client.models.generate_content(
            model=settings.gemini_model,
            contents=[uploaded_file, prompt],
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
            ),
        )
        logger.info("Received response from Gemini")
        return response.text
