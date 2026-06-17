# Odysseus: Trading Agent Container (Lightweight)
FROM python:3.12-slim

LABEL maintainer="Denis Mocchiutti"
LABEL description="Odysseus Trading Agent - Lightweight Isolated Container"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Rome
ENV PYTHONUNBUFFERED=1

# Minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Create app directories
RUN mkdir -p /app /workspace /app/config /app/logs

# Install minimal Python dependencies
RUN pip install --no-cache-dir \
    requests \
    aiohttp \
    python-dotenv

# Simple entrypoint
RUN echo '#!/bin/sh\necho "Odysseus Trading Agent"\necho "Workspace: /workspace"\necho "Ollama: $OLLAMA_HOST"\necho "Ready for trading..."\n/bin/sh\n' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

WORKDIR /app
ENTRYPOINT ["/app/entrypoint.sh"]
