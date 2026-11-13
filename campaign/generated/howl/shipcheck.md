# ShipCheck

Gate on explicit release-readiness checks.

```bash
#!/usr/bin/env bash
set -euo pipefail
"$KUJO" run "$RELEASES/shipcheck-source/shipcheck.kujo" \
  gate --dir "$RELEASES/shipcheck-source" --format json

```

**Concepts:** Verified with Kujo

A release checklist is easy to forget when shipping gets busy. Executed gate --format json against the pinned ShipCheck release checkout. This checks repository readiness signals, not test execution, artifact integrity, or release certification. Output shown here, when present, was observed in evidence/verified/shipcheck/stdout.txt. Full commands and artifacts are in the verification report.

---

Release prep should not depend on remembering every file. ShipCheck gates this pinned repo checkout on its readiness checks and returns JSON plus an exit code. It checks release signals; it does not run the project tests for you.

https://github.com/kujolang/shipcheck/blob/7eedd9e02d8730d65e06e16f4984d909d23539bc/README.md#gate-semantics

Kujo: Real examples. Recorded execution. Clear limits.
