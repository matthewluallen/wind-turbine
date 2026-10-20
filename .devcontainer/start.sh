#!/bin/bash
# Codespace start-up: bring the lab stack up reliably and leave a log behind.
#
# Runs as postStartCommand (every start/resume). Two things this fixes:
#  1. docker-in-docker's daemon can still be starting when postStartCommand fires,
#     so a bare "docker compose up -d" occasionally fails with "Cannot connect to
#     the Docker daemon" and nothing starts. We wait for the daemon first.
#  2. Nothing recorded what happened. Everything goes to .devcontainer/start.log.
#
# Port forwarding itself is declared in devcontainer.json ("forwardPorts"), so it
# no longer depends on Codespaces noticing the docker-proxy listeners.

LOG="$(dirname "$0")/start.log"
exec >>"$LOG" 2>&1
echo "=== start.sh $(date -u +%FT%TZ) ==="

# 1. wait for dockerd (up to 2 minutes)
for i in $(seq 1 60); do
  if docker info >/dev/null 2>&1; then
    echo "docker ready after $((i*2))s"
    break
  fi
  [ "$i" -eq 60 ] && { echo "ERROR: docker daemon not ready after 120s"; exit 1; }
  sleep 2
done

# 2. bring the stack up (idempotent; restart policy keeps it up across resumes)
cd "$(dirname "$0")/.." || exit 1
docker compose up -d --remove-orphans
echo "compose exit: $?"

# 3. report what is listening, for the Ports tab / troubleshooting
sleep 5
docker compose ps --format 'table {{.Service}}\t{{.Status}}\t{{.Ports}}'
echo "listening: $(ss -Htln 2>/dev/null | awk '{print $4}' | grep -E ':(1880|3000|8080|8090)$' | sort -u | tr '\n' ' ')"
echo "note: Turbine HMI (1880) waits for opensearch to pass its healthcheck; expect 2-4 min on a 2-core codespace."
