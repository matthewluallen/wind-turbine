#!/bin/bash

# Everything a Codespace needs is baked into images published under
# ghcr.io/matthewluallen/wind-turbine (see .github/workflows/images.yml), and
# weather.csv is a regular file in this repo. Nothing is downloaded from
# third-party sites here.

# If weather.csv is missing or is still a Git LFS pointer (an old clone), the
# simulation reports ZERO wind with no error -- which makes the AitM demo
# impossible to distinguish from reality. Fail loudly.
if [ ! -f configs/ot-sim/weather.csv ] || head -1 configs/ot-sim/weather.csv | grep -q 'git-lfs'; then
  echo ""
  echo "######################################################################"
  echo "# ERROR: weather.csv is missing or is a Git LFS pointer, not real data."
  echo "# The simulation will report ZERO wind and the attack will look"
  echo "# identical to normal operation."
  echo "#"
  echo "# Fix: pull the latest main branch (weather.csv is a regular file"
  echo "# there) and rebuild the Codespace. If it persists, tell the instructor."
  echo "######################################################################"
  echo ""
else
  echo "OK: weather.csv data present."
fi

docker compose pull wireshark main-ctlr opensearch grafana
