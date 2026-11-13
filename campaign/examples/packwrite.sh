#!/usr/bin/env bash
set -euo pipefail
"$RELEASES/packwrite-source/bin/packwrite" validate \
  --output agent --config packwrite.toml --json
"$RELEASES/packwrite-source/bin/packwrite" summary \
  --output agent --config packwrite.toml --json
