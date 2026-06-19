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
export KUJO
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/howl-cli-contract.XXXXXX")"

cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

check_output() {
    local label="$1"
    local expected="$2"
    shift 2

    local actual
    set +e
    actual="$("$@" 2>&1)"
    local command_status=$?
    set -e

    if [ "$command_status" -ne 0 ]; then
        echo "  FAIL: $label exited $command_status"
        printf '%s\n' "$actual"
        return 1
    fi

    if [ "$actual" != "$expected" ]; then
        echo "  FAIL: $label output changed"
        printf '%s\n' "$expected" > "$TMP_DIR/expected"
        printf '%s\n' "$actual" > "$TMP_DIR/actual"
        diff -u "$TMP_DIR/expected" "$TMP_DIR/actual" || true
        return 1
    fi

    return 0
}

check_failure() {
    local label="$1"
    local expected="$2"
    shift 2

    local actual
    set +e
    actual="$("$@" 2>&1)"
    local command_status=$?
    set -e

    if [ "$command_status" -eq 0 ]; then
        echo "  FAIL: $label exited 0"
        printf '%s\n' "$actual"
        return 1
    fi

    if [ "$actual" != "$expected" ]; then
        echo "  FAIL: $label output changed"
        printf '%s\n' "$expected" > "$TMP_DIR/expected"
        printf '%s\n' "$actual" > "$TMP_DIR/actual"
        diff -u "$TMP_DIR/expected" "$TMP_DIR/actual" || true
        return 1
    fi

    return 0
}

run_cli_contracts() {
    local cli_status=0

    local expected_validate='ok: howl.json is valid (3 card(s))'
    check_output "validate exact output" "$expected_validate" "$PROJECT_DIR/bin/howl" validate || cli_status=1

    local expected_list='clear-intent  —  Clear intent over boilerplate
    file: examples/clear-intent.kujo
    concepts: clear intent, agent-readable code, low-noise syntax
safe-refactor  —  Refactors that preserve behavior
    file: examples/safe-refactor.kujo
    concepts: behavior preservation, reviewable diffs, testable code
agent-handoff  —  Built for the next agent
    file: examples/agent-handoff.kujo
    concepts: safe agent collaboration, durable code, token-efficient'
    check_output "list exact output" "$expected_list" "$PROJECT_DIR/bin/howl" list || cli_status=1

    local expected_show='id:       clear-intent
title:    Clear intent over boilerplate
tagline:  Kujo favors code that humans and agents can continue safely.
file:     examples/clear-intent.kujo
language: kujo
concepts: clear intent, agent-readable code, low-noise syntax

--- code preview ---
# Clear intent over boilerplate.
# A tiny program that says what it does, with nothing extra.

func greet(name) {
    return "Ready, " + name
}

print(greet("agent"))


--- expected output ---
Ready, agent'
    check_output "show exact output" "$expected_show" "$PROJECT_DIR/bin/howl" show clear-intent || cli_status=1

    check_failure "missing option value" 'howl: --format requires a value' "$PROJECT_DIR/bin/howl" render --format || cli_status=1
    check_failure "invalid render format" 'howl: --format must be one of: all, svg, html, markdown' "$PROJECT_DIR/bin/howl" render --format png || cli_status=1
    check_failure "invalid positive integer" 'howl: --max-code-lines must be a positive integer' "$PROJECT_DIR/bin/howl" show clear-intent --max-code-lines 0 || cli_status=1
    check_failure "unsafe output dir" "howl: --out must be a safe directory path (not blank, root, '.', '..', traversal, or ambiguous segments)" "$PROJECT_DIR/bin/howl" render --out ../outside || cli_status=1

    return "$cli_status"
}

cd "$PROJECT_DIR"
set +e
"$KUJO" run "$PROJECT_DIR/tests/howl_test.kujo" -- "$PROJECT_DIR"
status=$?
set -e

# Clean up throwaway fixture dirs the test created under the project root.
find "$PROJECT_DIR" -maxdepth 1 -name 'tmp_test_*' -exec rm -rf {} + 2>/dev/null || true

if [ "$status" -eq 0 ]; then
    set +e
    KUJO="$KUJO" run_cli_contracts
    status=$?
    set -e
fi

if [ "$status" -eq 0 ]; then
    echo "tests: OK (exit 0)"
else
    echo "tests: FAILED (exit $status)"
fi
exit $status
