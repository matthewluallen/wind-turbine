#!/bin/bash

apt update && apt install -y git-lfs unzip python3 iproute2

git lfs pull

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

curl -L -o /tmp/opensearch.zip "https://grafana.com/api/plugins/grafana-opensearch-datasource/versions/2.13.0/download?os=linux&arch=amd64"
unzip -d configs/grafana/plugins /tmp/opensearch.zip

docker compose pull wireshark main-ctlr opensearch grafana
