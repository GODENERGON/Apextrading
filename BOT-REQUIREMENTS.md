# Odysseus Bot — Requirements & Architecture

## 🎯 Bot Purpose

Telegram interface for Odysseus trading agent. Remote control + interaction without SSH.

---

## 📋 Requirements

### Functional (What the bot does)
- [ ] **Start Odysseus** — Switch to trading mode via `/start_odysseus`
- [ ] **Stop Odysseus** — Return to OpenClaw via `/stop_odysseus`
- [ ] **Status check** — Get system state via `/status`
- [ ] **Send message** — Forward user input to Odysseus (chat mode)
- [ ] **View logs** — Stream recent container logs via `/logs`
- [ ] **Execute commands** — Run shell commands in container (optional, controlled)

### Non-Functional
- ✅ **Security** — Only Denis (147668366) can interact
- ✅ **Isolation** — Bot doesn't affect OpenClaw
- ✅ **Logging** — All interactions logged
- ✅ **Error handling** — Graceful failures, rollback on error
- ✅ **No resource contention** — Bot runs light, Odysseus gets resources

---

## 🏗️ Architecture

### Components

```
Telegram
    ↓
Bot Handler (Python/Node)
    ↓
API Server (localhost:8888)
    ↓
Odysseus Container
    ├── /workspace  (user input, logs)
    └── Ollama models (phi 3.5, qwen, gemma4)
```

### Communication Flow

1. **User sends message via Telegram**
2. **Bot handler receives via Telegram API**
3. **Bot forwards to API server** (REST POST)
4. **API server executes command in container** (docker exec)
5. **Result returned to bot**
6. **Bot sends response via Telegram**

### Technology Stack

| Layer | Tech | Rationale |
|---|---|---|
| Bot | Python + python-telegram-bot | Same as OpenClaw bot, familiar |
| API Server | FastAPI (lightweight, async) | Fast, minimal deps, easy to containerize |
| Container Communication | docker exec + socket | Simple, no extra services needed |
| Transport | REST + JSON | Standard, no complex setup |

---

## 📦 Deployment Model

### Option A: Bot runs on HOST (NUC)
```
HOST:
├── OpenClaw (systemd)
├── Odysseus (docker)
└── odysseus-bot (systemd) ← NEW

Communication: Bot → Docker API → Odysseus
Pros: Simple, shared token with ApexGreenhouse
Cons: One more service to manage
```

### Option B: Bot runs INSIDE Odysseus container
```
ODYSSEUS CONTAINER:
├── App workspace
├── Odysseus core
└── Bot API server ← NEW

Communication: Telegram → HOST:8888 → Container
Pros: All together, clean separation
Cons: Need to expose port from container
```

**Recommendation:** **Option A** (Bot on HOST)
- Keeps Odysseus clean and stateless
- Bot can control Odysseus lifecycle
- Easier to debug and update

---

## 🔌 API Endpoints (inside container)

Bot will call these endpoints on Odysseus container:

```
POST /api/status
  Response: { "status": "running/stopped", "uptime": "...", "memory": "..." }

POST /api/message
  Request: { "text": "user message" }
  Response: { "result": "...", "timestamp": "..." }

POST /api/logs
  Request: { "lines": 50 }
  Response: { "logs": ["line1", "line2", ...] }

POST /api/execute
  Request: { "command": "python trade.py" }
  Response: { "stdout": "...", "stderr": "...", "exit_code": 0 }

POST /api/stop
  Response: { "status": "stopping", "message": "..." }
```

---

## 🔐 Security

### Authentication
- Bot token (from Telegram BotFather) ✅
- User ID whitelist (147668366 only) ✅
- API key for container endpoint (optional, token in env var) ⚠️

### Isolation
- Bot runs as `godener` user
- Docker socket accessed via docker CLI (no direct socket)
- Container workdir isolated (`/workspace`)
- No access to sensitive OpenClaw data

### Logging
- All commands logged to `/home/godener/odysseus/logs/bot-*.log`
- User input sanitized before logging
- Errors logged but don't expose internals

---

## 📝 Conversation Flow

**Example: User asks Odysseus to run a trade**

```
Denis (Telegram): "What's the current price of BTC?"

Bot handler: Receives message, validates user (✓ Denis)

API Server: POST /api/message { "text": "..." }

Odysseus Container: Processes via LLM (Ollama), returns result

Bot: Receives { "result": "Current BTC price is $45,000..." }

Telegram: Denis gets response
```

---

## 🚀 Phases

### Phase 1: Setup
- [ ] Create bot project structure in Apextrading
- [ ] Define API server spec (FastAPI skeleton)
- [ ] Plan Telegram bot handler
- [ ] Create logging/error handling

### Phase 2: Implement API Server
- [ ] FastAPI app with endpoints
- [ ] Docker integration (docker exec)
- [ ] Logging
- [ ] Error handling

### Phase 3: Implement Bot
- [ ] Telegram handler (python-telegram-bot)
- [ ] User auth (Denis only)
- [ ] Command parsing
- [ ] Response formatting

### Phase 4: Integration & Testing
- [ ] Bot ↔ API server communication test
- [ ] API server ↔ Container test
- [ ] Full end-to-end test
- [ ] Error scenarios test
- [ ] Rollback test

---

## ✅ Success Criteria

- [x] Bot receives Telegram messages from Denis
- [x] Bot commands (start, stop, status) work reliably
- [x] Chat mode passes messages to Odysseus
- [x] OpenClaw remains unaffected
- [x] Logs are clean and informative
- [x] Rollback always possible
- [x] No resource contention

---

## 📚 Repository Structure

```
/home/godener/odysseus/
├── bot/                      ← NEW
│   ├── telegram_handler.py
│   ├── api_server.py
│   ├── config.py
│   ├── requirements.txt
│   └── README.md
├── Dockerfile
├── docker-compose.yml
├── orchestrate.sh
└── ...existing files
```

---

**Next:** Phase 1 (Setup) → detailed project structure & planning
