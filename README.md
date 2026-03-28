# PDF Data Extraction & Mapping Application

A web application that extracts data from German roller shutter order PDFs, maps fields using deterministic rules, and outputs a tab-separated `.txt` file.

## Architecture

```
Frontend (HTML/CSS/JS) → FastAPI → Celery Worker → Gemini API
                                 ↓
                              Redis (broker/backend)
```

- **Gemini 2.5 Flash** handles PDF visual layout extraction
- **Pure Python** applies deterministic mapping rules for 100% reliability
- **Celery + Redis** for async PDF processing
- **FastAPI** serves the API and static frontend

## Quick Start (Docker)

### Prerequisites
- Docker & Docker Compose
- A Google Gemini API key

### Run

```bash
# 1. Clone the repository
git clone <repo-url>
cd llm-pdf-extraction-app

# 2. Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Start all services
docker compose up --build
```

The app will be available at **http://localhost:8000**

### Docker Pull

```bash
docker pull <your-dockerhub-username>/llm-pdf-extraction-app:latest
```

## Services

| Service | Purpose | Port |
|---------|---------|------|
| `llm-api` | FastAPI web server | 8000 |
| `llm-worker` | Celery worker for PDF processing | — |
| `llm-redis` | Redis broker/backend | 6379 |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload` | Upload a PDF for processing |
| `GET` | `/api/v1/status/{task_id}` | Poll task processing status |
| `GET` | `/api/v1/result/{task_id}` | Get extracted + mapped data as JSON |
| `GET` | `/api/v1/download/{task_id}` | Download generated `.txt` file |

## Processing Pipeline

1. **Extract** — Gemini reads the PDF and returns structured JSON
2. **Validate** — Auto-correct OCR typos, check data consistency
3. **Map** — Apply deterministic rules (Rollladen→SILBER, Endleiste→hwf9006, etc.)
4. **Generate** — Build tab-separated TXT with header (11 cols) + position rows (10 cols)

## Development

### Run Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

### Run Locally (without Docker)

```bash
# Start Redis
redis-server

# Start API
uvicorn src.main:app --reload --port 8000

# Start Worker (separate terminal)
celery -A src.celery_app:celery_app worker --loglevel=info
```

## Project Structure

```
src/
├── main.py              # FastAPI app entry point
├── config.py            # Settings via pydantic-settings
├── celery_app.py        # Celery instance config
├── api/v1/              # API route handlers (thin controllers)
├── services/            # All business logic
├── schemas/             # Pydantic models
├── tasks/               # Celery task wrappers
└── static/              # Frontend (HTML/CSS/JS)
tests/                   # Unit + integration + API tests
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | — |
| `REDIS_URL` | Redis connection URL | `redis://llm-redis:6379/0` |
