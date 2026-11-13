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

I would rather put the release checklist in a command than keep it in my head. ShipCheck looks for the repo signals I need before shipping and gives me JSON plus a gate exit code. Here is the small example to try in a local checkout.

https://github.com/kujolang/shipcheck/blob/7eedd9e02d8730d65e06e16f4984d909d23539bc/README.md#gate-semantics

Verified with Kujo: Real examples. Recorded execution. Clear limits.
