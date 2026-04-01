"""Application-wide constants."""

import re

# HTTP status code to machine-readable error name mapping
HTTP_STATUS_NAMES: dict[int, str] = {
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    429: "rate_limit_exceeded",
}

# Celery state to API status mapping
CELERY_STATE_MAP: dict[str, str] = {
    "PENDING": "PENDING",
    "STARTED": "PROCESSING",
    "SUCCESS": "COMPLETED",
    "FAILURE": "FAILED",
}

# Supported file types for document ingestion
ALLOWED_EXTENSIONS: set[str] = {
    ".pdf", ".docx", ".pptx", ".txt", ".md", ".csv",
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp",
}

IMAGE_EXTENSIONS: set[str] = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

# File extension to MIME type mapping
MIME_MAP: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".tiff": "image/tiff",
    ".bmp": "image/bmp",
    ".pdf": "application/pdf",
}

# Supported LLM providers
SUPPORTED_LLM_PROVIDERS: set[str] = {"google"}

# ── Upload limits ──
MAX_UPLOAD_SIZE_MB: int = 10
MAX_UPLOAD_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# ── OCR/LLM typo corrections ──
TYPO_CORRECTIONS: dict[str, str] = {
    "Weift": "Weiß",
    "Weiss": "Weiß",
    "Weißt": "Weiß",
    "Eicktro": "Elektro",
    "Elekro": "Elektro",
    "Eletro": "Elektro",
}

# ── Validation domain constants ──
KNOWN_ROLLLADEN_VALUES: set[str] = {
    "Aluminium Silber",
    "Aluminium Anthrazit",
    "Aluminium Weiß",
}
KNOWN_ANTRIEB_KEYWORDS: set[str] = {"SMI", "IO", "IO-homecontrol"}
ENDLEISTE_PATTERN: re.Pattern[str] = re.compile(r"(9006|7016|9016)$")
DATE_PATTERN: re.Pattern[str] = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
BEMERKUNG_MM_PATTERN: re.Pattern[str] = re.compile(r"(\d+)\s*mm", re.IGNORECASE)

# ── TXT output column ordering ──
HEADER_COLUMNS: list[str] = [
    "lieferanschrift",
    "kommission",
    "rollladennummer",
    "liefertermin",
    "rollladen",
    "konstruktion",
    "konstruktion_nummer",
    "aussenschuerze",
    "endleiste",
    "antrieb",
    "gesamt",
]

POSITION_COLUMNS: list[str] = [
    "line",
    "stueck",
    "breite",
    "hoehe",
    "links",
    "rechts",
    "antrieb",
    "pos",
    "bemerkung",
    "bemerkung_nummer",
]
