# Eval

Turn workflow expectations into checks.

```bash
#!/usr/bin/env bash
set -euo pipefail
"$KUJO" run "$RELEASES/eval-source/main.kujo" run \
  "$CAMPAIGN/inputs/eval.json" --output-dir "$OUTPUT" --json

```

**Concepts:** Verified with Kujo

A successful command alone is not a complete release smoke check. Executed the unchanged canonical three-check release suite against its copied kennel.toml fixture. This checks a command, file existence, and file size; it does not evaluate model quality. Output shown here, when present, was observed in evidence/verified/eval/stdout.txt. Full commands and artifacts are in the verification report.

---

Here is a small Eval suite you can actually run: check that a command succeeds, that a manifest exists, and that the file clears a size check. Three explicit checks, with JSON results ready for the next step in your workflow.

https://github.com/kujolang/eval/blob/71e66dff780d6930bcbe093c046bf31aa26411df/examples/release&#95;gate&#95;suite.json

Verified with Kujo: Real examples. Recorded execution. Clear limits.
