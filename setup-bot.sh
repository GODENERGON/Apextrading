#!/bin/bash
# Odysseus Bot Setup & Installation
# Run once to install bot as systemd service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_DIR="$SCRIPT_DIR/bot"
SERVICE_FILE="$SCRIPT_DIR/odysseus-bot.service"
SERVICE_TARGET="/etc/systemd/system/odysseus-bot.service"

echo "=========================================="
echo "Odysseus Bot — Setup & Installation"
echo "=========================================="
echo ""

# Check prerequisites
echo "1. Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✓ Python 3 available"

if ! command -v systemctl &> /dev/null; then
    echo "❌ systemctl not found"
    exit 1
fi
echo "✓ systemctl available"

# Check .env file
if [ ! -f "$BOT_DIR/.env" ]; then
    echo "❌ .env file not found at $BOT_DIR/.env"
    echo "   Please copy .env.example and fill in the values"
    exit 1
fi
echo "✓ .env file exists"

# Check token is set
if grep -q "TELEGRAM_BOT_TOKEN=\*\*\*" "$BOT_DIR/.env"; then
    echo "❌ TELEGRAM_BOT_TOKEN not configured in .env"
    exit 1
fi
echo "✓ TELEGRAM_BOT_TOKEN is set"

# Install dependencies
echo ""
echo "2. Installing Python dependencies..."
pip3 install -q -r "$BOT_DIR/requirements.txt" || {
    echo "❌ Failed to install dependencies"
    exit 1
}
echo "✓ Dependencies installed"

# Copy systemd service
echo ""
echo "3. Installing systemd service..."
if [ -f "$SERVICE_TARGET" ]; then
    echo "⚠ Service file already exists, backing up..."
    sudo cp "$SERVICE_TARGET" "$SERVICE_TARGET.bak.$(date +%s)"
fi

sudo cp "$SERVICE_FILE" "$SERVICE_TARGET" || {
    echo "❌ Failed to copy service file"
    exit 1
}
sudo chmod 644 "$SERVICE_TARGET"
echo "✓ Service file installed"

# Reload systemd
echo ""
echo "4. Reloading systemd..."
sudo systemctl daemon-reload || {
    echo "❌ Failed to reload systemd"
    exit 1
}
echo "✓ systemd reloaded"

# Enable service
echo ""
echo "5. Enabling service..."
sudo systemctl enable odysseus-bot.service || {
    echo "❌ Failed to enable service"
    exit 1
}
echo "✓ Service enabled (will start on boot)"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the bot:"
echo "   sudo systemctl start odysseus-bot"
echo ""
echo "2. Check status:"
echo "   sudo systemctl status odysseus-bot"
echo ""
echo "3. View logs:"
echo "   journalctl -u odysseus-bot -f"
echo ""
echo "4. Stop the bot:"
echo "   sudo systemctl stop odysseus-bot"
echo ""
echo "Make sure Odysseus container is running before starting the bot:"
echo "   docker compose -f $SCRIPT_DIR/docker-compose.yml up -d"
echo ""
echo "=========================================="
