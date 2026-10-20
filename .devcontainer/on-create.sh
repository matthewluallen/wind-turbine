#!/bin/bash
# onCreateCommand. IMPORTANT: this script must never exit non-zero. If any
# lifecycle command fails, Codespaces skips the ones after it -- including
# postStartCommand -- and the lab stack never starts (the codespace "works" but
# no ports ever appear). So every step is best-effort and the script ends with
# exit 0; start.sh (postStartCommand) pulls anything still missing.
set +e
LOG="$(dirname "$0")/on-create.log"; exec > >(tee -a "$LOG") 2>&1
echo "=== on-create.sh $(date -u +%FT%TZ) ==="

export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get install -y git-lfs unzip python3 iproute2 curl

git lfs install --skip-repo
git lfs pull || echo "WARN: git lfs pull failed (see check below)"

# --- LFS verification (added) -------------------------------------------------
# git lfs pull can fail silently (network, or the repo's LFS bandwidth quota
# being exhausted by a whole class). If it did, weather.csv is still a pointer
# (or missing entirely) and the simulation reports ZERO wind with no error --
# which makes the AitM demo impossible to distinguish from reality. Fail loudly.
if [ ! -f configs/ot-sim/weather.csv ] || head -1 configs/ot-sim/weather.csv | grep -q 'git-lfs'; then
  echo ""
  echo "######################################################################"
  echo "# ERROR: weather.csv is missing or still a Git LFS pointer -- the real"
  echo "# data did NOT download. The simulation will report ZERO wind and the"
  echo "# attack will look identical to normal operation."
  echo "#"
  echo "# Fix: run   git lfs pull   again."
  echo "# If it keeps failing, the repo LFS bandwidth quota may be exhausted"
  echo "# (tell the instructor) -- or git-lfs is not installed in this env."
  echo "######################################################################"
  echo ""
else
  echo "OK: weather.csv LFS data present."
fi
# -----------------------------------------------------------------------------

if curl -fsSL -o /tmp/opensearch.zip "https://grafana.com/api/plugins/grafana-opensearch-datasource/versions/2.13.0/download?os=linux&arch=amd64"; then
  unzip -o -q -d configs/grafana/plugins /tmp/opensearch.zip && echo "OK: grafana opensearch plugin installed"
else
  echo "WARN: grafana opensearch plugin download failed; Grafana will start without it"
fi

# docker-in-docker's daemon may still be starting; wait before pulling (up to 2 min)
for i in $(seq 1 60); do docker info >/dev/null 2>&1 && break; sleep 2; done
docker info >/dev/null 2>&1 || echo "WARN: docker not ready during on-create; start.sh will pull on first start"
docker compose pull wireshark main-ctlr opensearch grafana || echo "WARN: image pull failed; start.sh will retry"

echo "=== on-create.sh done $(date -u +%FT%TZ) ==="
exit 0
