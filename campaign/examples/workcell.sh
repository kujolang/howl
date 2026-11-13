#!/usr/bin/env bash
set -euo pipefail
"$RELEASES/workcell-source/bin/workcell" validate \
  --file "$CAMPAIGN/inputs/workcell.json"
"$RELEASES/workcell-source/bin/workcell" inspect \
  --file "$CAMPAIGN/inputs/workcell.json" \
  --repo "$CAMPAIGN/.." --summary
