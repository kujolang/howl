#!/usr/bin/env bash
set -euo pipefail
"$KUJO" run "$RELEASES/shipcheck-source/shipcheck.kujo" \
  gate --dir "$RELEASES/shipcheck-source" --format json
