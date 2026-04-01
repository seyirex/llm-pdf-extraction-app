/**
 * RollDocs — PDF Data Extraction & Mapping Frontend
 * Handles upload, polling, results rendering, and download.
 */
(function () {
    "use strict";

    const API_BASE = "/api/v1";
    const POLL_INTERVAL_MS = 2000;

    // DOM Elements
    const uploadSection = document.getElementById("upload-section");
    const processingSection = document.getElementById("processing-section");
    const resultsSection = document.getElementById("results-section");
    const errorSection = document.getElementById("error-section");

    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const processingStep = document.getElementById("processing-step");
    const progressBar = document.getElementById("progress-bar");
    const warningsContainer = document.getElementById("warnings-container");
    const headerTableBody = document.querySelector("#header-table tbody");
    const positionsTableHead = document.querySelector("#positions-table thead tr");
    const positionsTableBody = document.querySelector("#positions-table tbody");
    const extractedJson = document.getElementById("extracted-json");
    const mappedJson = document.getElementById("mapped-json");
    const downloadBtn = document.getElementById("download-btn");
    const newUploadBtn = document.getElementById("new-upload-btn");
    const retryBtn = document.getElementById("retry-btn");
    const errorMessage = document.getElementById("error-message");
    const navbarStatus = document.getElementById("navbar-status");
    const pdfIframe = document.getElementById("pdf-iframe");
    const pdfPreviewDetails = document.getElementById("pdf-preview-details");
    const authControls = document.getElementById("auth-controls");
    const authModeLabel = document.getElementById("auth-mode-label");
    const apiKeyInput = document.getElementById("api-key-input");
    const saveApiKeyBtn = document.getElementById("save-api-key-btn");

    // Summary elements
    const summaryPositions = document.getElementById("summary-positions");
    const summaryTotal = document.getElementById("summary-total");
    const summaryWarnings = document.getElementById("summary-warnings");

    let currentTaskId = null;
    let pollTimer = null;
    let authEnabled = false;
    let authHeaderName = "x-api-key";

    const STORAGE_API_KEY = "rolldocs_api_key";

    // ===== State Management =====
    function showSection(section) {
        [uploadSection, processingSection, resultsSection, errorSection].forEach(
            (s) => { s.hidden = true; }
        );
        section.hidden = false;
    }

    function setNavbarStatus(label, state) {
        const dot = navbarStatus.querySelector(".status-dot");
        const text = navbarStatus.querySelector(".status-label");
        text.textContent = label;
        dot.style.background =
            state === "processing" ? "var(--accent)" :
            state === "error" ? "var(--error)" :
            state === "success" ? "var(--success)" :
            "var(--success)";
    }

    function showError(message) {
        errorMessage.textContent = message;
        setNavbarStatus("Error", "error");
        showSection(errorSection);
    }

    function getApiKey() {
        return (apiKeyInput && apiKeyInput.value ? apiKeyInput.value.trim() : "");
    }

    function ensureApiKeyConfigured() {
        if (!authEnabled) return true;

        const key = getApiKey();
        if (key) return true;

        showError("API key is required. Enter it in the top-right field and try again.");
        if (apiKeyInput) apiKeyInput.focus();
        return false;
    }

    function buildAuthHeaders() {
        if (!authEnabled) return {};
        const key = getApiKey();
        return key ? { [authHeaderName]: key } : {};
    }

    async function apiFetch(path, options = {}) {
        const headers = {
            ...(options.headers || {}),
            ...buildAuthHeaders(),
        };

        const response = await fetch(`${API_BASE}${path}`, {
            ...options,
            headers,
        });

        if (response.status === 401) {
            showError("Unauthorized. Check your API key and try again.");
        }

        return response;
    }

    async function initializeAuth() {
        try {
            const response = await fetch(`${API_BASE}/auth/config`);
            if (!response.ok) return;

            const payload = await response.json();
            const data = payload.data || {};
            authEnabled = parseEnabledFlag(data.enabled);
            authHeaderName = String(data.header_name || "x-api-key");

            if (!authControls || !apiKeyInput || !authModeLabel) return;
            authModeLabel.textContent = authEnabled ? "Auth On" : "Auth Off";

            if (authEnabled) {
                authControls.hidden = false;
                const savedKey = localStorage.getItem(STORAGE_API_KEY) || "";
                apiKeyInput.value = savedKey;
            } else {
                authControls.hidden = true;
            }
        } catch (err) {
            // Keep app usable if auth config endpoint is unavailable.
        }
    }

    function saveApiKey() {
        if (!apiKeyInput) return;
        localStorage.setItem(STORAGE_API_KEY, getApiKey());
    }

    function parseEnabledFlag(value) {
        if (typeof value === "boolean") return value;
        if (typeof value === "string") {
            return ["1", "true", "yes", "on"].includes(value.toLowerCase());
        }
        return Boolean(value);
    }

    function resetApp() {
        currentTaskId = null;
        if (pollTimer) clearInterval(pollTimer);
        pollTimer = null;
        fileInput.value = "";
        progressBar.style.width = "0%";
        pdfIframe.src = "";
        if (pdfPreviewDetails) pdfPreviewDetails.open = false;
        setNavbarStatus("Ready", "ready");
        showSection(uploadSection);
    }

    // ===== Upload =====
    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("drag-over");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("drag-over");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("drag-over");
        const files = e.dataTransfer.files;
        if (files.length > 0) handleFile(files[0]);
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) handleFile(fileInput.files[0]);
    });

    async function handleFile(file) {
        if (!file.name.toLowerCase().endsWith(".pdf")) {
            showError("Please select a PDF file.");
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showError("File exceeds the 10MB size limit.");
            return;
        }

        if (!ensureApiKeyConfigured()) return;

        showSection(processingSection);
        setNavbarStatus("Processing", "processing");
        updateProgressSteps(null);
        progressBar.style.width = "5%";
        processingStep.textContent = "Uploading PDF...";

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await apiFetch("/upload", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            if (!response.ok || !data.success) {
                showError(data.message || data.error || "Upload failed");
                return;
            }

            currentTaskId = data.data.task_id;
            progressBar.style.width = "15%";
            processingStep.textContent = "Processing started...";
            startPolling();
        } catch (err) {
            showError("Failed to upload file. Please try again.");
        }
    }

    // ===== Polling =====
    function startPolling() {
        pollTimer = setInterval(pollStatus, POLL_INTERVAL_MS);
    }

    async function pollStatus() {
        if (!currentTaskId) return;

        try {
            const response = await apiFetch(`/status/${currentTaskId}`);
            const data = await response.json();
            const result = data.data || {};

            if (result.status === "SUCCESS") {
                clearInterval(pollTimer);
                pollTimer = null;
                progressBar.style.width = "100%";
                await loadResults();
                return;
            }

            if (result.status === "FAILURE") {
                clearInterval(pollTimer);
                pollTimer = null;
                showError("Processing failed. Please try again with a different PDF.");
                return;
            }

            if (result.step) {
                const stepLabels = {
                    extracting: "Extracting data from PDF...",
                    validating: "Validating extracted data...",
                    retrying_extraction: "Retrying extraction...",
                    mapping: "Applying mapping rules...",
                    generating: "Generating output file...",
                };
                const stepProgress = {
                    extracting: "30%",
                    validating: "50%",
                    retrying_extraction: "45%",
                    mapping: "70%",
                    generating: "85%",
                };
                processingStep.textContent =
                    stepLabels[result.step] || "Processing...";
                progressBar.style.width =
                    stepProgress[result.step] || "20%";
                updateProgressSteps(result.step);
            }
        } catch (err) {
            // Keep polling on network errors
        }
    }

    function updateProgressSteps(currentStep) {
        const steps = document.querySelectorAll(".progress-steps .step");
        const connectors = document.querySelectorAll(".progress-steps .step-connector");
        const stepOrder = ["extracting", "validating", "mapping", "generating"];
        const currentIdx = stepOrder.indexOf(currentStep);

        steps.forEach((stepEl) => {
            const step = stepEl.dataset.step;
            const idx = stepOrder.indexOf(step);

            stepEl.classList.remove("active", "done");
            if (currentStep && idx < currentIdx) {
                stepEl.classList.add("done");
            } else if (step === currentStep) {
                stepEl.classList.add("active");
            }
        });

        connectors.forEach((conn, idx) => {
            conn.classList.remove("done");
            if (currentStep && idx < currentIdx) {
                conn.classList.add("done");
            }
        });
    }

    // ===== Results =====
    async function loadResults() {
        try {
            const response = await apiFetch(`/result/${currentTaskId}`);
            const data = await response.json();
            if (!response.ok || !data.success) {
                showError(data.message || "Failed to load results.");
                return;
            }

            renderResults(data.data);
            const pdfKeyQuery = authEnabled && getApiKey()
                ? `?api_key=${encodeURIComponent(getApiKey())}`
                : "";
            pdfIframe.src = `${API_BASE}/pdf/${currentTaskId}${pdfKeyQuery}`;
            if (pdfPreviewDetails) pdfPreviewDetails.open = false;
            setNavbarStatus("Complete", "success");
            showSection(resultsSection);
        } catch (err) {
            showError("Failed to load results.");
        }
    }

    function renderResults(data) {
        // Summary strip
        const mappedPositions = data.mapped.positions || [];
        const totalUnits = mappedPositions.reduce(
            (sum, p) => sum + (parseInt(p.stueck, 10) || 0), 0
        );
        const allWarnings = [
            ...(data.warnings || []),
            ...(data.corrections || []).map((c) => `Auto-corrected: ${c}`),
        ];

        summaryPositions.textContent = mappedPositions.length;
        summaryTotal.textContent = totalUnits;
        summaryWarnings.textContent = allWarnings.length;

        // Warnings
        if (allWarnings.length > 0) {
            warningsContainer.hidden = false;
            warningsContainer.innerHTML = `
                <h4>Validation Notes</h4>
                <ul>${allWarnings.map((w) => `<li>${escapeHtml(w)}</li>`).join("")}</ul>
            `;
        } else {
            warningsContainer.hidden = true;
        }

        // Header table
        const extractedHeader = data.extracted.header || {};
        const mappedHeader = data.mapped.header || {};
        const headerFields = [
            "lieferanschrift", "kommission", "rollladennummer", "liefertermin",
            "rollladen", "konstruktion", "konstruktion_nummer", "aussenschuerze",
            "endleiste", "antrieb", "gesamt",
        ];

        headerTableBody.innerHTML = headerFields
            .map(
                (field) => `
                <tr>
                    <td><strong>${escapeHtml(field)}</strong></td>
                    <td>${escapeHtml(String(extractedHeader[field] || ""))}</td>
                    <td>${escapeHtml(String(mappedHeader[field] || ""))}</td>
                </tr>`
            )
            .join("");

        // Positions table
        const positionCols = [
            { key: "line", label: "line" },
            { key: "stueck", label: "stueck" },
            { key: "breite", label: "breite" },
            { key: "hoehe", label: "hoehe" },
            { key: "links", label: "L" },
            { key: "rechts", label: "R" },
            { key: "antrieb", label: "antrieb" },
            { key: "pos", label: "pos" },
            { key: "bemerkung", label: "bemerkung" },
            { key: "bemerkung_nummer", label: "bemerkung_nummer" },
        ];

        positionsTableHead.innerHTML = positionCols
            .map((col) => `<th>${escapeHtml(col.label)}</th>`)
            .join("");

        positionsTableBody.innerHTML = mappedPositions
            .map(
                (pos) => `
                <tr>${positionCols
                    .map((col) => `<td>${escapeHtml(String(pos[col.key] || ""))}</td>`)
                    .join("")}</tr>`
            )
            .join("");

        // JSON views
        extractedJson.textContent = JSON.stringify(data.extracted, null, 2);
        mappedJson.textContent = JSON.stringify(data.mapped, null, 2);
    }

    // ===== Tabs =====
    document.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));

            btn.classList.add("active");
            const tabId = btn.dataset.tab + "-view";
            document.getElementById(tabId).classList.add("active");
        });
    });

    // ===== Download =====
    downloadBtn.addEventListener("click", async () => {
        if (!currentTaskId) return;
        if (!ensureApiKeyConfigured()) return;

        try {
            const response = await apiFetch(`/download/${currentTaskId}`);
            if (!response.ok) {
                showError("Failed to download TXT file.");
                return;
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `output_${currentTaskId}.txt`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            showError("Failed to download TXT file.");
        }
    });

    // ===== Reset =====
    newUploadBtn.addEventListener("click", resetApp);
    retryBtn.addEventListener("click", resetApp);

    if (saveApiKeyBtn) {
        saveApiKeyBtn.addEventListener("click", saveApiKey);
    }

    if (apiKeyInput) {
        apiKeyInput.addEventListener("keydown", (event) => {
            if (event.key === "Enter") saveApiKey();
        });
    }

    initializeAuth();

    // ===== Utils =====
    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }
})();
