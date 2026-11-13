# Lens

Check desktop and mobile; keep evidence.

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$RELEASES/lens-source"
./lens check "$LENS_URL/dashboard/" \
  --spec "$CAMPAIGN/inputs/dashboard.json" \
  --html --accessibility --check-links --out "$OUTPUT"

```

**Expected output:**

```text
Lens completed: PASS
Report: /Users/robertdevore/2026/Kujolang/kujo-repos/howl/campaign/evidence/verified/lens/artifacts/lens-report.md
```

**Concepts:** Verified with Kujo

A page can look fine at one size and still have console or layout problems. Executed a local dashboard fixture with desktop/mobile screenshots, accessibility and link checks. Adapted the canonical spec by removing unsupported not&#95;exists. No accessibility certification or production-site coverage is claimed. Output shown here, when present, was observed in evidence/verified/lens/stdout.txt. Full commands and artifacts are in the verification report.

---

“Looks fine here” is not much evidence. Lens checked this local dashboard at desktop and mobile sizes, applied the supported spec assertions, and saved screenshots plus reports. Useful handoff material without an LLM judging the page.

https://github.com/kujolang/lens/blob/85778065ca329c93293b387a0e7011437b6d0c60/examples/specs/dashboard.json

Kujo: Real examples. Recorded execution. Clear limits.
