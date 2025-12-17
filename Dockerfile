FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install minimal OS dependencies (mostly for SSL certificates and pip)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src ./src

# Create non-root user
RUN useradd --system --create-home --home-dir /nonroot stash_exporter && \
    chown -R stash_exporter:stash_exporter /app

USER stash_exporter

# Sensible defaults – can be overridden at runtime
ENV EXPORTER_LISTEN_PORT=9100 \
    SCRAPE_INTERVAL_SECONDS=30

EXPOSE 9100

# Run the exporter
CMD ["python", "-m", "src.main"]


