#!/usr/bin/env bash
# Test runner for Howl.
#
# Exercises the manifest model, renderers, caption logic, and gallery through
# the Kujo interpreter with throwaway fixtures under a temp dir. No network,
# no global state. The pass/fail verdict is the process exit code (0 = all
# assertions passed); the printed summary is informational only.
#
# Override the interpreter with KUJO, e.g.
#   KUJO=/path/to/kujo/target/release/kujo tests/run.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KUJO="${KUJO:-kujo}"

cd "$PROJECT_DIR"
set +e
"$KUJO" run "$PROJECT_DIR/tests/howl_test.kujo" -- "$PROJECT_DIR"
status=$?
set -e

# Clean up throwaway fixture dirs the test created under the project root.
find "$PROJECT_DIR" -maxdepth 1 -name 'tmp_test_*' -exec rm -rf {} + 2>/dev/null || true

if [ "$status" -eq 0 ]; then
    echo "tests: OK (exit 0)"
else
    echo "tests: FAILED (exit $status)"
fi
exit $status
