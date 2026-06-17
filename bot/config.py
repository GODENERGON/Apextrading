"""
Odysseus Bot Configuration
"""

import os
from pathlib import Path

# Paths
BOT_DIR = Path(__file__).parent
PROJECT_ROOT = BOT_DIR.parent
LOGS_DIR = PROJECT_ROOT / "logs"
WORKSPACE_DIR = PROJECT_ROOT / "data"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
WORKSPACE_DIR.mkdir(exist_ok=True)

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID", "147668366"))

# API Server (inside Odysseus container)
API_HOST = os.getenv("ODYSSEUS_API_HOST", "localhost")
API_PORT = int(os.getenv("ODYSSEUS_API_PORT", "8888"))
API_URL = f"http://{API_HOST}:{API_PORT}"
API_TIMEOUT = int(os.getenv("ODYSSEUS_API_TIMEOUT", "30"))

# Docker
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "odysseus-trading")
DOCKER_SOCKET = "/var/run/docker.sock"

# Logging
LOG_FILE = LOGS_DIR / "odysseus-bot.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Features
ENABLE_MESSAGE_FORWARDING = os.getenv("ENABLE_MESSAGE_FORWARDING", "true").lower() == "true"
ENABLE_COMMAND_EXECUTION = os.getenv("ENABLE_COMMAND_EXECUTION", "false").lower() == "true"
MAX_LOG_LINES = int(os.getenv("MAX_LOG_LINES", "100"))

# Timeouts
MESSAGE_TIMEOUT = int(os.getenv("MESSAGE_TIMEOUT", "30"))
STATUS_CHECK_INTERVAL = int(os.getenv("STATUS_CHECK_INTERVAL", "5"))

# Debug
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

print(f"✓ Config loaded: API={API_URL}, Container={CONTAINER_NAME}, User={TELEGRAM_ALLOWED_USER_ID}")
