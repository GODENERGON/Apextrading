# Apextrading — Odysseus Trading Agent

**Isolated Trading Agent deployment on NUC8i7BEH**

Odysseus is a dedicated trading agent running in an isolated Docker container, alongside OpenClaw production system. This repository contains the deployment configuration, orchestration scripts, and documentation.

## Architecture

```
NUC8i7BEH (32GB RAM, 8 core)
├── OpenClaw (native systemd) — PRODUCTION, untouched
└── Odysseus (docker container) — TRADING, on-demand
    ├── Network: isolated bridge (172.28.0.0/16)
    ├── CPU limit: 4 cores max
    ├── RAM limit: 16GB max
    └── Ollama access: localhost:11434 (shared)
```

## Quick Start

### Prerequisites
- Docker & Docker Compose installed
- OpenClaw running (systemd service)
- Ollama running (localhost:11434)

### Build Odysseus Image
```bash
cd /home/godener/odysseus
docker build -t odysseus:latest .
```

### Switch to Odysseus Mode
```bash
./orchestrate.sh odysseus
```

This will:
1. Gracefully stop OpenClaw
2. Start Odysseus container with isolated resources
3. Enable access to Ollama and shared vault

### Switch Back to OpenClaw
```bash
./orchestrate.sh openclaw
```

### Check Status
```bash
./orchestrate.sh status
```

## File Structure

```
/home/godener/odysseus/
├── config/              # Odysseus configuration files
├── data/                # Odysseus workspace
├── logs/                # Orchestration logs
├── docker-compose.yml   # Container orchestration
├── Dockerfile           # Container image spec
├── orchestrate.sh       # Safe switching script
└── README.md            # This file
```

## Orchestration Scripts

### `orchestrate.sh`
Safe switching between OpenClaw and Odysseus modes.

```bash
./orchestrate.sh openclaw   # → Production mode (OpenClaw active)
./orchestrate.sh odysseus   # → Trading mode (Odysseus active)
./orchestrate.sh status     # → Show system state
./orchestrate.sh prod       # → Alias for openclaw
./orchestrate.sh trading    # → Alias for odysseus
```

**Features:**
- Graceful shutdown (no kill -9)
- Health checks after startup
- Logging to `logs/orchestrate-*.log`
- Rollback path always available

## Docker Configuration

### Resource Limits (cgroups)
- **CPU:** 4 cores max / 2 cores reserved
- **RAM:** 16GB max / 8GB reserved
- No interference with OpenClaw when not running

### Network
- Bridge network: `odysseus-net` (172.28.0.0/16)
- Access to host Ollama via `host.docker.internal:11434`
- Isolated from system network

### Volume Mounts
- `/home/godener/odysseus/data` → `/workspace` (RW)
- `/home/godener/vault` → `/vault` (RO, for safety)
- `/home/godener/odysseus/logs` → `/app/logs` (RW)
- `/home/godener/odysseus/config` → `/app/config` (RW)

## LLM Integration

Odysseus accesses local LLM models via Ollama:
- Phi 3.5 (primary)
- Qwen 2.5 7B (fallback 1)
- Gemma 4 26B (fallback 2)
- Claude Sonnet 4.6 (fallback 3, paid)

**Access:** `OLLAMA_HOST=http://host.docker.internal:11434`

## Safety & Rollback

### Backup
Config backup stored at: `~/vault/backups/openclaw-config-20260617-*.tar.gz`

### Rollback if Issues
```bash
# Restore OpenClaw config
tar -xzf ~/vault/backups/openclaw-config-*.tar.gz

# Restart OpenClaw
systemctl restart openclaw

# Stop Odysseus container
docker-compose down --remove-orphans
```

## Development

### Add to Odysseus Config
Place custom configs in `config/` directory.

### Logs
Orchestration logs: `logs/orchestrate-*.log`
Container logs: View with `docker-compose logs`

## Deployment Phases

- [x] **Phase 1:** Preparation (directory structure, docker-compose, scripts)
- [ ] **Phase 2:** Testing (build image, test isolation, verify connectivity)
- [ ] **Phase 3:** Go-Live (final deployment, monitoring)

## Related Documentation

- `ODYSSEUS-PLAN.md` — Detailed implementation plan
- `docker-compose.yml` — Container orchestration spec
- `Dockerfile` — Container image specification
- `orchestrate.sh` — Orchestration logic

## License

Private repository — Apextrading/Odysseus project

---

**Last updated:** 2026-06-17  
**Repository:** https://github.com/GODENERGON/Apextrading  
**Maintainer:** Denis Mocchiutti
