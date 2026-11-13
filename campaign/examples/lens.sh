#!/usr/bin/env bash
set -euo pipefail
cd "$RELEASES/lens-source"
./lens check "$LENS_URL/dashboard/" \
  --spec "$CAMPAIGN/inputs/dashboard.json" \
  --html --accessibility --check-links --out "$OUTPUT"
