# Odysseus Bot — Telegram Interface

Remote control for Odysseus trading agent via Telegram.

## 📋 Features

- ✅ Start/stop Odysseus trading mode
- ✅ System status checks
- ✅ Message forwarding to Odysseus
- ✅ Container log access
- ✅ Secure (Denis only)
- ✅ Async operation
- ✅ Comprehensive logging

## 🏗️ Architecture

```
Telegram User (Denis)
        ↓
  Bot Handler (telegram_handler.py)
        ↓
  API Client (api_client.py)
        ↓
  Odysseus API Server (localhost:8888)
        ↓
  Odysseus Container
```

**Note:** API server inside Odysseus container is coming in Phase 2.

## 🚀 Quick Start

### Setup

```bash
cd /home/godener/odysseus/bot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your-bot-token-here"
export TELEGRAM_ALLOWED_USER_ID="147668366"  # Denis only
export ODYSSEUS_API_HOST="localhost"
export ODYSSEUS_API_PORT="8888"
export LOG_LEVEL="INFO"
```

### Run

```bash
python3 main.py
```

Or as a service:

```bash
# Create bot service
sudo systemctl edit odysseus-bot.service

# Add:
[Unit]
Description=Odysseus Telegram Bot
After=docker.service

[Service]
Type=simple
User=godener
WorkingDirectory=/home/godener/odysseus/bot
Environment="TELEGRAM_BOT_TOKEN=..."
Environment="ODYSSEUS_API_HOST=localhost"
Environment="ODYSSEUS_API_PORT=8888"
ExecStart=/usr/bin/python3 /home/godener/odysseus/bot/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable odysseus-bot
sudo systemctl start odysseus-bot
```

## 📱 Commands

### `/start_odysseus`
Start trading mode. Gracefully shuts down OpenClaw, starts Odysseus with full resources.

```
/start_odysseus
→ ✅ Odysseus Starting
  Status: running
  Trading mode active. Full resources allocated.
```

### `/stop_odysseus`
Stop trading mode. Gracefully shuts down Odysseus, restarts OpenClaw.

```
/stop_odysseus
→ ✅ Returning to OpenClaw
  Status: stopped
  OpenClaw restored to production mode.
```

### `/status`
Get system status: which agent is running, memory, CPU, uptime.

```
/status
→ 📊 System Status
  OpenClaw: 🟢 RUNNING
  Odysseus: 🔴 STOPPED
  Memory: 1.0GB
  CPU: 45min
  Uptime: 1d 18h
```

### `/logs`
Get recent container logs.

```
/logs
→ 📋 Recent Logs
  [log lines...]
```

### `/help`
Show this help message.

## 💬 Message Forwarding

Just send a regular message and the bot will forward it to Odysseus for processing.

```
User: "What's the current BTC price?"
→ Odysseus processes via LLM
→ Bot: "💬 Odysseus Response: Current BTC price is $45,000..."
```

**Note:** Requires ENABLE_MESSAGE_FORWARDING=true and API server running.

## 🔐 Security

- **User whitelist:** Only Denis (147668366) can interact
- **Logging:** All interactions logged to `/home/godener/odysseus/logs/odysseus-bot.log`
- **Isolation:** Bot doesn't access OpenClaw directly
- **API auth:** Can add API key (env var) for container endpoint

## 📁 Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point |
| `config.py` | Configuration & environment |
| `telegram_handler.py` | Telegram bot logic (commands, messages) |
| `api_client.py` | HTTP client for Odysseus API server |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

## 🔧 Configuration

Set via environment variables (see `config.py`):

```bash
# Telegram
TELEGRAM_BOT_TOKEN=...
TELEGRAM_ALLOWED_USER_ID=147668366

# API Server (inside Odysseus container)
ODYSSEUS_API_HOST=localhost
ODYSSEUS_API_PORT=8888
ODYSSEUS_API_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
DEBUG=false

# Features
ENABLE_MESSAGE_FORWARDING=true
ENABLE_COMMAND_EXECUTION=false
MAX_LOG_LINES=100
```

## 📊 Logging

All interactions logged to:
```
/home/godener/odysseus/logs/odysseus-bot.log
```

View:
```bash
tail -f /home/godener/odysseus/logs/odysseus-bot.log
```

## 🐛 Troubleshooting

### Bot doesn't respond
- Check TELEGRAM_BOT_TOKEN is set
- Check API server is running (inside container)
- Check logs: `tail -f /home/godener/odysseus/logs/odysseus-bot.log`

### API connection fails
- Check Odysseus container is running: `/home/godener/odysseus/orchestrate.sh status`
- Check API server is listening on 8888: `curl http://localhost:8888/api/status`

### Unauthorized access
- Only Denis (ID 147668366) can interact with bot
- Check your Telegram user ID

## 🚀 Next Phase

Phase 2: Implement API server inside Odysseus container:
- FastAPI endpoints for all commands
- Docker integration (docker exec)
- Logging and error handling
- Full integration testing

---

**Status:** Phase 1 (Bot structure, handlers, client) ✅  
**Next:** Phase 2 (API server, integration)
