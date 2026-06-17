"""
Odysseus Bot - Telegram Handler
Remote interface for Odysseus trading agent
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_ALLOWED_USER_ID,
    LOG_FILE,
    LOG_LEVEL,
    ENABLE_MESSAGE_FORWARDING,
)
from api_client import OdysseusAPIClient

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

# API client
api_client = OdysseusAPIClient()


def auth_required(func):
    """Decorator: Check if user is authorized"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != TELEGRAM_ALLOWED_USER_ID:
            await update.message.reply_text(
                f"❌ Unauthorized. Only Denis can interact with Odysseus.\n"
                f"(Your ID: {user_id})"
            )
            logger.warning(f"Unauthorized access attempt from user {user_id}")
            return
        return await func(update, context)
    return wrapper


@auth_required
async def cmd_start_odysseus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start Odysseus trading mode"""
    await update.message.chat.send_action(ChatAction.TYPING)
    logger.info("User requested: start odysseus")
    
    try:
        result = await api_client.start_odysseus()
        await update.message.reply_text(
            f"✅ **Odysseus Starting**\n\n"
            f"Status: {result.get('status', 'unknown')}\n"
            f"Message: {result.get('message', 'started')}\n\n"
            f"Trading mode active. Full resources allocated."
        )
        logger.info("Odysseus started successfully")
    except Exception as e:
        await update.message.reply_text(f"❌ Error starting Odysseus:\n{str(e)}")
        logger.error(f"Error starting Odysseus: {e}")


@auth_required
async def cmd_stop_odysseus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop Odysseus and return to OpenClaw"""
    await update.message.chat.send_action(ChatAction.TYPING)
    logger.info("User requested: stop odysseus")
    
    try:
        result = await api_client.stop_odysseus()
        await update.message.reply_text(
            f"✅ **Returning to OpenClaw**\n\n"
            f"Status: {result.get('status', 'unknown')}\n"
            f"Message: {result.get('message', 'stopped')}\n\n"
            f"OpenClaw restored to production mode."
        )
        logger.info("Odysseus stopped, OpenClaw restored")
    except Exception as e:
        await update.message.reply_text(f"❌ Error stopping Odysseus:\n{str(e)}")
        logger.error(f"Error stopping Odysseus: {e}")


@auth_required
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get system status"""
    await update.message.chat.send_action(ChatAction.TYPING)
    logger.info("User requested: status")
    
    try:
        status = await api_client.get_status()
        openclaw_status = "🟢 RUNNING" if status.get("openclaw_active") else "🔴 STOPPED"
        odysseus_status = "🟢 RUNNING" if status.get("odysseus_active") else "🔴 STOPPED"
        
        await update.message.reply_text(
            f"📊 **System Status**\n\n"
            f"OpenClaw: {openclaw_status}\n"
            f"Odysseus: {odysseus_status}\n\n"
            f"Memory: {status.get('memory', 'N/A')}\n"
            f"CPU: {status.get('cpu', 'N/A')}\n"
            f"Uptime: {status.get('uptime', 'N/A')}"
        )
        logger.info(f"Status check: openclaw={status.get('openclaw_active')}, odysseus={status.get('odysseus_active')}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting status:\n{str(e)}")
        logger.error(f"Error getting status: {e}")


@auth_required
async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get recent logs from Odysseus container"""
    await update.message.chat.send_action(ChatAction.TYPING)
    logger.info("User requested: logs")
    
    try:
        logs = await api_client.get_logs()
        log_text = "\n".join(logs[-50:])  # Last 50 lines
        
        if log_text:
            await update.message.reply_text(f"📋 **Recent Logs**\n\n```\n{log_text}\n```")
        else:
            await update.message.reply_text("No logs available yet.")
        
        logger.info("Logs retrieved")
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting logs:\n{str(e)}")
        logger.error(f"Error getting logs: {e}")


@auth_required
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    help_text = """
🤖 **Odysseus Bot Commands**

/start_odysseus - Start trading mode
/stop_odysseus - Return to OpenClaw
/status - System status
/logs - Recent container logs
/help - This message

**Usage:**
Just send a message and I'll forward it to Odysseus for processing.
"""
    await update.message.reply_text(help_text)
    logger.info("Help shown")


@auth_required
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward user messages to Odysseus"""
    if not ENABLE_MESSAGE_FORWARDING:
        return
    
    user_text = update.message.text
    logger.info(f"Message from user: {user_text[:50]}...")
    
    await update.message.chat.send_action(ChatAction.TYPING)
    
    try:
        result = await api_client.send_message(user_text)
        response = result.get("result", "No response")
        
        await update.message.reply_text(f"💬 **Odysseus Response**\n\n{response}")
        logger.info(f"Message processed, response sent")
    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n{str(e)}")
        logger.error(f"Error processing message: {e}")


async def start_bot():
    """Start the Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set!")
    
    logger.info("Starting Odysseus Bot...")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start_odysseus", cmd_start_odysseus))
    app.add_handler(CommandHandler("stop_odysseus", cmd_stop_odysseus))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("help", cmd_help))
    
    # Message handler (forward to Odysseus)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot handlers registered")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    logger.info("✅ Odysseus Bot is running and polling for messages")


if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())
