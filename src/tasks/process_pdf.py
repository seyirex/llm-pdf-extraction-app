"""Celery task for PDF processing — thin wrapper around pipeline_service."""

from pathlib import Path

from src.celery_app import celery_app
from src.utils.logger import get_logger

logger = get_logger()
from src.services.pipeline_service import run_pipeline


@celery_app.task(bind=True, name="process_pdf")
def process_pdf_task(self, pdf_path_str: str, output_path_str: str) -> dict:
    """Process a PDF through the extraction-mapping pipeline.

    Args:
        pdf_path_str: String path to the uploaded PDF file.
        output_path_str: String path for the generated TXT output file.

    Returns:
        Dict with pipeline results including extracted data, mapped data,
        warnings, corrections, and output file path.
    """
    pdf_path = Path(pdf_path_str)
    output_path = Path(output_path_str)

    def update_progress(step: str) -> None:
        """Update Celery task state with current pipeline step."""
        self.update_state(state="PROGRESS", meta={"step": step})

    logger.info(f"Starting PDF processing task: {pdf_path.name}")

    try:
        result = run_pipeline(
            pdf_path=pdf_path,
            output_path=output_path,
            on_progress=update_progress,
        )

        return {
            "status": "completed",
            "extracted": result.extracted.model_dump(),
            "mapped": result.mapped.model_dump(),
            "warnings": result.warnings,
            "corrections": result.corrections,
            "txt_path": str(result.txt_path),
        }
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        raise
