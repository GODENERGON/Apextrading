# Odysseus: Trading Agent Container
# Base: Ubuntu 24.04 (aligned with NUC)

FROM ubuntu:24.04

LABEL maintainer="Denis Mocchiutti"
LABEL description="Odysseus Trading Agent - Isolated Container"

# Setup environment
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Rome

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    build-essential \
    libssl-dev \
    libffi-dev \
    tzdata \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app directories
RUN mkdir -p /app /workspace /app/config /app/logs

# Set up Python environment
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python trading dependencies
RUN pip install --upgrade pip && \
    pip install \
    requests \
    numpy \
    pandas \
    python-dotenv \
    aiohttp

# Install Node.js global tools (if needed)
RUN npm install -g pm2

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "Odysseus Trading Agent (Container)"\n\
echo "Workspace: /workspace"\n\
echo "Vault (shared): /vault"\n\
echo "Ollama: $OLLAMA_HOST"\n\
echo ""\n\
echo "Ready for trading operations..."\n\
/bin/bash\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

WORKDIR /app
ENTRYPOINT ["/app/entrypoint.sh"]
