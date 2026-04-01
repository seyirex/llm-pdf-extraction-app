# Plan: Add Side-by-Side PDF Preview to Results UI

## Context
The app currently lets users upload PDFs for data extraction but never shows the original PDF back to the user while reviewing results. A side-by-side layout lets users compare the source PDF and extracted output at the same time for faster validation.

## Approach
Use a two-pane results layout:
- Left pane: persistent PDF preview (`<iframe>`)
- Right pane: existing output area with tabs for "Table View" and "JSON View"

This avoids placing PDF in a separate tab and enables continuous side-by-side comparison. The browser's built-in PDF renderer is sufficient; no external PDF library is needed.

## Changes

### 1. Backend: `get_pdf_path` method — `src/services/task_service.py`
- Add a `get_pdf_path(task_id)` method mirroring `get_download_path`
- Checks Celery state isn't PENDING (prevents enumeration with random IDs)
- Constructs path: `Path(settings.upload_dir) / f"{task_id}.pdf"`
- Verifies file exists on disk, raises `AppException` if not

### 2. Backend: New endpoint — `src/api/v1/pdf.py` (NEW FILE)
- `GET /api/v1/pdf/{task_id}` — returns uploaded PDF via `FileResponse`
- Follows exact pattern of `download.py` (dependency injection, error handling)
- Uses `media_type="application/pdf"`, **no** `filename` param (so browser renders inline, not downloads)

### 3. Backend: Register router — `src/api/v1/__init__.py`
- Import `pdf` module and `router.include_router(pdf.router)`

### 4. Frontend: HTML — `src/static/index.html`
- Replace current single results content flow with a split container:
	- `#results-split-layout` wrapper
	- Left: `#pdf-panel` containing iframe
	- Right: `#data-panel` containing existing tab buttons and views (`#table-view`, `#json-view`)
- Remove need for a standalone "PDF Preview" tab button

### 5. Frontend: CSS — `src/static/css/styles.css`
- Add split layout styles:
	- `.results-split-layout { display: grid; grid-template-columns: 1fr 1fr; gap: ... }`
	- `.pdf-panel` and `.data-panel` with matching card styling
	- `.pdf-iframe` fills panel height (`min-height` around `70vh`)
- Responsive behavior:
	- At tablet/mobile breakpoints, collapse to single column (PDF first, data second)
	- Reduce iframe height for smaller screens

### 6. Frontend: JS — `src/static/js/app.js`
- Add `pdfIframe` DOM reference
- Set `pdfIframe.src` in `loadResults` after `renderResults()` call
- Clear `pdfIframe.src = ""` in `resetApp()`
- Keep existing table/JSON tab switching logic for the data pane
- Ensure split layout container is shown/hidden together with existing results state

### 7. Tests — `tests/test_api.py`
- Add `TestPdfEndpoint` class with success/not-found/file-missing tests
- Follows existing `TestDownloadEndpoint` pattern

## Verification
1. `docker compose up --build` to rebuild
2. Upload a PDF and wait for processing to complete
3. Results screen should show PDF on the left and data panel on the right (desktop)
4. Switch between "Table View" and "JSON View" while PDF remains visible
5. On mobile/tablet widths, layout should stack vertically and remain usable
6. Click "New Upload" — PDF iframe should clear
7. Run tests: `docker compose run --rm llm-api pytest tests/`
