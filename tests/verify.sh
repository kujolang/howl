#!/usr/bin/env bash
# One offline gate for source, CLI/filesystem contracts, and artifact snapshots.
set -euo pipefail
cd "$(dirname "$0")/.."
export KUJO="${KUJO:-kujo}"
for source in src/*.kujo howl.kujo tests/howl_test.kujo examples/*.kujo; do
  "$KUJO" check "$source"
done
bash -n bin/howl tests/run.sh tests/verify.sh .github/scripts/check-kujo-tool-artifacts.sh
./tests/run.sh
python3 tests/release_regression.py --site howl=howl.json
