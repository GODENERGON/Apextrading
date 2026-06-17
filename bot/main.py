#!/usr/bin/env python3
"""
Odysseus Bot - Main Entry Point
"""

import logging
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import LOG_FILE, LOG_LEVEL, TELEGRAM_BOT_TOKEN
from telegram_handler import start_bot

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("=" * 60)
    logger.info("ODYSSEUS BOT STARTUP")
    logger.info("=" * 60)
    
    # Validate config
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
        logger.error("Please set: export TELEGRAM_BOT_TOKEN='your-token-here'")
        sys.exit(1)
    
    logger.info("✓ Configuration valid")
    logger.info("✓ Starting bot...")
    
    try:
        await start_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
