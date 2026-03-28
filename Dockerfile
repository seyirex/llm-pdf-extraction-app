# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV APP_PORT=8083

# Set work directory
WORKDIR /app

# Copy runtime requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create directories for data, uploads, and cache
RUN mkdir -p /app/data /app/data/uploads

# Copy application code
COPY src/ ./src/

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE ${APP_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import os,sys,urllib.request; port=os.getenv('APP_PORT','8083'); urllib.request.urlopen('http://localhost:%s/health' % port, timeout=5); sys.exit(0)"

# Run the application
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${APP_PORT}"