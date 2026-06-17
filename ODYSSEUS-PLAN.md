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

### Phase 2: Testing (Isolated) ✅ DONE
- [x] Build Odysseus docker image (sandboxed test) ✓
  - Base: `python:3.12-slim` (lightweight)
  - Size: 229MB disk, 56.3MB content
  - Build time: ~2 minutes
  - Tag: `odysseus:latest`
- [x] Spin container in dry-run (don't persist) ✓
  - Container startup: OK
  - Status: Up 27 seconds (clean shutdown)
  - No persistent data leftover
- [x] Test Ollama connectivity from container ✓
  - Network bridge: working (172.28.0.0/16)
  - host.docker.internal: reachable
  - No connectivity issues detected
- [x] Verify no port conflicts with OpenClaw ✓
  - No port clashes
  - OpenClaw unaffected (1.0G RAM, stable)
  - Isolation verified

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

## Status: Phase 1 & 2 Complete ✅ ✅

**Timeline:**
- Phase 1: Completed (all prep files, GitHub repo)
- Phase 2: Completed (image build, container test, isolation verified)

**System Health:**
- ✅ OpenClaw: RUNNING (1.0G RAM, 1d 18h uptime, stable)
- ✅ Odysseus image: READY (`odysseus:latest`, 229MB, slim)
- ✅ Container test: PASSED (network isolated, no conflicts)
- ✅ Repository: SYNCED (https://github.com/GODENERGON/Apextrading)
- ✅ Rollback: READY

## Next Move
**Phase 3: Go-Live (Controlled Deployment)**
- Create systemd service for odysseus (optional)
- Test `orchestrate.sh` switching (openclaw ↔ odysseus)
- Final pre-flight check
- Ready for production use

Proceed with Phase 3?
