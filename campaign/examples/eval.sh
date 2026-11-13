#!/usr/bin/env bash
set -euo pipefail
"$KUJO" run "$RELEASES/eval-source/main.kujo" run \
  "$CAMPAIGN/inputs/eval.json" --output-dir "$OUTPUT" --json
