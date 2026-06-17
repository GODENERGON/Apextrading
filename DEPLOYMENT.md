# Odysseus Bot — Production Deployment Guide

**Status:** Ready for Production 🚀  
**Date:** 2026-06-17

---

## ✅ Pre-Deployment Checklist

- [x] Docker image built and tested
- [x] API server implemented and responding
- [x] Bot handler implemented
- [x] API client working (asyncio)
- [x] Configuration system ready
- [x] OdysseusBot token obtained (894481…OtRU)
- [x] systemd service created
- [x] Setup script created
- [x] Virtual environment working
- [x] Bot → API communication tested
- [x] All endpoints verified

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start Odysseus Container (with API Server)
```bash
cd /home/godener/odysseus

# Start container with API on port 8888
docker run -d --name odysseus-api -p 8888:8888 odysseus:latest

# Verify API is working
curl -X POST http://localhost:8888/api/status
```

### Step 2: Install Bot as Systemd Service
```bash
cd /home/godener/odysseus

# Run setup script
./setup-bot.sh

# This will:
# - Check prerequisites
# - Install Python dependencies (in venv)
# - Copy systemd service file
# - Enable the service
```

### Step 3: Start Bot Service
```bash
# Start bot
sudo systemctl start odysseus-bot

# Check status
sudo systemctl status odysseus-bot

# View logs
journalctl -u odysseus-bot -f
```

---

## 🔍 Verification

### Check Container
```bash
docker ps | grep odysseus-api
curl -X POST http://localhost:8888/api/status
```

### Check Bot Service
```bash
sudo systemctl status odysseus-bot
journalctl -u odysseus-bot -n 20
```

### Check Both Together
```bash
# Container should return status
curl -X POST http://localhost:8888/api/status

# Bot should be running and polling Telegram
journalctl -u odysseus-bot -f
```

---

## 📱 Using the Bot (Telegram)

**Bot URL:** t.me/ApexOdyssesusBot

### Commands
```
/start_odysseus   - Start trading mode (stops OpenClaw gracefully)
/stop_odysseus    - Return to OpenClaw (stops Odysseus)
/status           - System status (memory, uptime, who's active)
/logs             - Recent container logs
/help             - Show this help

Free messages     - Forward to Odysseus via Ollama models
                   (phi3.5, qwen2.5, gemma4)
```

### Usage Example
```
You (Telegram): "/status"
↓
Bot polls Telegram
↓
OdysseusBot receives message
↓
Validates user (Denis only, 147668366)
↓
Sends POST http://localhost:8888/api/status
↓
API server returns:
  {
    "status": "ok",
    "openclaw_active": false,
    "odysseus_active": true,
    "memory": "1.2G",
    "uptime": "1 hour 23 minutes"
  }
↓
Bot formats and sends to Telegram
↓
You receive: "📊 System Status
             OpenClaw: 🔴 STOPPED
             Odysseus: 🟢 RUNNING
             Memory: 1.2G
             Uptime: 1h 23m"
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Telegram
TELEGRAM_BOT_TOKEN=894481…OtRU  (from BotFather)
TELEGRAM_ALLOWED_USER_ID=147668366  (Denis only)

# API Server (inside container)
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

File location: `/home/godener/odysseus/bot/.env`

---

## 📊 Architecture

```
┌─────────────────────────────────────┐
│ Telegram (t.me/ApexOdyssesusBot)   │
└────────────┬────────────────────────┘
             │
      ┌──────▼──────┐
      │ OdysseusBot │
      │ Handler     │
      │ (systemd)   │
      └──────┬──────┘
             │
      ┌──────▼──────────────┐
      │ API Client (async)  │
      └──────┬──────────────┘
             │
         HOST:8888
             │
      ┌──────▼────────────┐
      │ ODYSSEUS CONTAINER│
      │    :8888          │
      │                   │
      │ FastAPI Server    │
      │ ├─ /api/status    │
      │ ├─ /api/message   │
      │ ├─ /api/logs      │
      │ └─ ...            │
      └──────┬────────────┘
             │
      ┌──────▼────────────┐
      │ OLLAMA:11434      │
      │ ├─ phi3.5:latest  │
      │ ├─ qwen2.5:7b     │
      │ └─ gemma4:26b     │
      └───────────────────┘
```

---

## 🛡️ Security

- **User Authentication:** Only Denis (147668366) can interact
- **Logging:** All commands logged to `/var/log/syslog` (journalctl)
- **Isolation:** Bot runs as user `godener`, no root access
- **Container:** Isolated network, read-only vault mount
- **API:** No external exposure (localhost:8888 only)

---

## 🔄 Systemd Service Management

### Start
```bash
sudo systemctl start odysseus-bot
```

### Stop
```bash
sudo systemctl stop odysseus-bot
```

### Restart
```bash
sudo systemctl restart odysseus-bot
```

### Enable (auto-start on boot)
```bash
sudo systemctl enable odysseus-bot
```

### Disable (don't auto-start)
```bash
sudo systemctl disable odysseus-bot
```

### View Status
```bash
sudo systemctl status odysseus-bot
```

### View Logs
```bash
# Last 50 lines
journalctl -u odysseus-bot -n 50

# Follow in real-time
journalctl -u odysseus-bot -f

# Since boot
journalctl -u odysseus-bot --boot

# Specific time range
journalctl -u odysseus-bot --since "2026-06-17 17:00:00"
```

---

## 🔧 Troubleshooting

### Bot doesn't respond in Telegram
1. Check bot is running: `sudo systemctl status odysseus-bot`
2. Check logs: `journalctl -u odysseus-bot -f`
3. Verify token in `.env`: `grep TELEGRAM_BOT_TOKEN /home/godener/odysseus/bot/.env`
4. Restart: `sudo systemctl restart odysseus-bot`

### API connection fails
1. Check container: `docker ps | grep odysseus`
2. Test API: `curl -X POST http://localhost:8888/api/status`
3. Check container logs: `docker logs odysseus-api`
4. Restart container: `docker restart odysseus-api`

### Port 8888 in use
```bash
# Find what's using it
lsof -i :8888

# Kill the process
kill -9 <PID>

# Restart container
docker restart odysseus-api
```

### Python venv issues
```bash
cd /home/godener/odysseus/bot

# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📈 Monitoring

### Check System Health
```bash
# Container
docker ps
docker stats odysseus-api

# Bot service
sudo systemctl status odysseus-bot

# OpenClaw (should be running)
sudo systemctl status openclaw

# Disk space
df -h /home/godener/odysseus
```

### View Recent Activity
```bash
# Bot logs
journalctl -u odysseus-bot --since "1 hour ago"

# Container logs
docker logs --tail 100 odysseus-api

# System logs
journalctl -f
```

---

## 🚀 Deployment Phases

✅ Phase 1: Bot handler & API client  
✅ Phase 2: API server implementation  
✅ Phase 3: Integration & testing  
🟢 Phase 4: Production deployment  
⏳ Future: Monitoring, alerting, advanced features

---

## 📝 Notes

- **OpenClaw:** Always running (production). Odysseus doesn't interfere.
- **Odysseus:** Starts on-demand via bot commands (`/start_odysseus`, `/stop_odysseus`)
- **API Server:** Runs inside Odysseus container, only accessible from localhost:8888
- **Bot:** Systemd service, auto-restarts on failure, runs as `godener` user

---

## 📞 Support

**Repository:** https://github.com/GODENERGON/Apextrading  
**Bot:** t.me/ApexOdyssesusBot  
**Issues:** Check logs, restart services, verify configuration

---

**Ready to deploy.** 🚀
