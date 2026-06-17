# Odysseus Hybrid Architecture — Safety Plan

## Current Baseline
- **OpenClaw:** systemd service, running since 2026-06-15 20:51
- **Status:** Stable (992MB RAM, 1d 11h uptime)
- **Config backup:** openclaw-config-20260617-081857.tar.gz ✅

## Architecture: Hybrid (Safe)

```
NUC8i7BEH
├── OpenClaw (native systemd) — PRODUCTION, untouched
├── Odysseus (docker container) — isolated box
└── Shared resources:
    ├── Ollama (localhost:11434) — accessible from container
    ├── /home/godener/vault — mounted RO/RW as needed
    └── cgroups isolation (CPU, RAM limits)
```

## Implementation Steps (SAFE PATH)

### Phase 1: Preparation (Zero Risk) ✅ DONE
- [x] Create Odysseus directory structure (`~/odysseus/`) ✓
  ```
  /home/godener/odysseus/
  ├── config/       # Odysseus config files
  ├── data/         # Odysseus workspace
  ├── logs/         # Runtime logs
  ├── docker-compose.yml  # Container orchestration
  ├── Dockerfile    # Build image (draft)
  └── orchestrate.sh      # Safe switching scripts
  ```
- [x] Plan docker-compose setup (draft only, don't build yet) ✓
  - Network isolation (172.28.0.0/16)
  - Resource limits: 4 CPU, 16GB RAM max
  - Ollama access via host.docker.internal:11434
  - Mount: /workspace (RW), /vault (RO), /logs (RW)
- [x] Create orchestration scripts (bash, non-destructive) ✓
  - `orchestrate.sh openclaw` → prod mode (stop Odysseus, start OpenClaw)
  - `orchestrate.sh odysseus` → trading mode (stop OpenClaw, start Odysseus)
  - `orchestrate.sh status` → show system state
- [x] Document container network config ✓

### Phase 2: Testing (Isolated)
- [ ] Build Odysseus docker image (sandboxed test)
- [ ] Spin container in dry-run (don't persist)
- [ ] Test Ollama connectivity from container
- [ ] Verify no port conflicts with OpenClaw

### Phase 3: Go-Live (Controlled)
- [ ] Create overlay systemd service for odysseus
- [ ] Add orchestration script (`/usr/local/bin/odysseus-mode` / `openclaw-mode`)
- [ ] Run test cycle (OpenClaw stays running)
- [ ] Only IF clean → full deploy

### Rollback Plan (If anything breaks)
```bash
systemctl restart openclaw           # Restart if anything hangs
tar -xzf backups/openclaw-config-*.tar.gz  # Restore config
# Container is safe to delete if needed
```

## Status: Phase 1 Complete ✅

All prep files created (non-destructive, no build yet):
- Docker images NOT built
- OpenClaw still running untouched
- Rollback path clear

## Next Move
**Phase 2: Testing (Isolated)**
- Build Odysseus image (dry-run, no persist)
- Test network connectivity
- Verify Ollama access from container
- Check for port conflicts

Ready to proceed with Phase 2?
