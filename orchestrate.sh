#!/bin/bash
# Odysseus Orchestration Script
# Safe switching between OpenClaw and Odysseus

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/logs/orchestrate-$(date +%Y%m%d-%H%M%S).log"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
  echo "[ERROR] $1" | tee -a "$LOG_FILE"
  exit 1
}

# Check prerequisites
check_docker() {
  if ! command -v docker &> /dev/null; then
    error "Docker not found. Install Docker first."
  fi
  log "✓ Docker available"
}

# Check OpenClaw status
check_openclaw() {
  if systemctl is-active --quiet openclaw; then
    log "✓ OpenClaw is running (PID: $(systemctl show -p MainPID --value openclaw))"
    return 0
  else
    log "⚠ OpenClaw is not running"
    return 1
  fi
}

# Check Odysseus container status
check_odysseus() {
  if docker ps -a --format '{{.Names}}' | grep -q "odysseus-trading"; then
    if docker ps --format '{{.Names}}' | grep -q "odysseus-trading"; then
      log "✓ Odysseus container is running"
      return 0
    else
      log "⚠ Odysseus container exists but is stopped"
      return 1
    fi
  else
    log "⚠ Odysseus container doesn't exist"
    return 1
  fi
}

# Gracefully stop OpenClaw
stop_openclaw() {
  log "→ Stopping OpenClaw..."
  if systemctl is-active --quiet openclaw; then
    systemctl stop openclaw || error "Failed to stop OpenClaw"
    sleep 2
    log "✓ OpenClaw stopped"
  else
    log "⚠ OpenClaw not running"
  fi
}

# Restart OpenClaw
start_openclaw() {
  log "→ Starting OpenClaw..."
  systemctl start openclaw || error "Failed to start OpenClaw"
  sleep 3
  check_openclaw || error "OpenClaw failed to start"
  log "✓ OpenClaw restarted"
}

# Start Odysseus container
start_odysseus() {
  log "→ Starting Odysseus container..."
  cd "$SCRIPT_DIR"
  docker-compose up -d || error "Failed to start Odysseus container"
  sleep 2
  check_odysseus || error "Odysseus container failed to start"
  log "✓ Odysseus container running"
}

# Stop Odysseus container
stop_odysseus() {
  log "→ Stopping Odysseus container..."
  cd "$SCRIPT_DIR"
  docker-compose down --remove-orphans || error "Failed to stop Odysseus"
  sleep 2
  log "✓ Odysseus container stopped"
}

# Mode: OpenClaw (default production)
mode_openclaw() {
  log "=== Switching to OPENCLAW mode ==="
  stop_odysseus || true
  start_openclaw
  log "✓ OpenClaw mode active"
}

# Mode: Odysseus (trading)
mode_odysseus() {
  log "=== Switching to ODYSSEUS mode ==="
  stop_openclaw
  start_odysseus
  log "✓ Odysseus mode active"
}

# Show status
mode_status() {
  log "=== System Status ==="
  check_openclaw || true
  check_odysseus || true
  check_docker
}

# Main
main() {
  check_docker
  
  case "${1:-status}" in
    openclaw|prod)
      mode_openclaw
      ;;
    odysseus|trading)
      mode_odysseus
      ;;
    status)
      mode_status
      ;;
    *)
      echo "Usage: $0 {openclaw|odysseus|status|prod|trading}"
      echo ""
      echo "  openclaw   → Stop Odysseus, start OpenClaw (production)"
      echo "  odysseus   → Stop OpenClaw, start Odysseus (trading mode)"
      echo "  status     → Show system status"
      echo "  prod       → Alias for openclaw"
      echo "  trading    → Alias for odysseus"
      exit 0
      ;;
  esac
}

mkdir -p "$SCRIPT_DIR/logs"
main "$@"
