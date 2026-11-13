#!/usr/bin/env bash
set -euo pipefail
ledger="$OUTPUT/ledger"
"$RELEASES/runledger-source/bin/runledger" start \
  --provider local --model scripted-example \
  --task "Record a showcase run" --repo "$CAMPAIGN/.." \
  --ledger "$ledger"
id=$(basename "$ledger"/runs/*.json .json)
"$RELEASES/runledger-source/bin/runledger" finish "$id" \
  --status pass --verdict "Receipt lifecycle exercised" --ledger "$ledger"
"$RELEASES/runledger-source/bin/runledger" report \
  --ledger "$ledger" --output "$OUTPUT/report.md"
"$RELEASES/runledger-source/bin/runledger" verify --ledger "$ledger" --json
