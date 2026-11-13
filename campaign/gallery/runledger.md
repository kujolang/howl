# RunLedger

Keep a run receipt after the chat ends.

```bash
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

```

**Expected output:**

```text
Started run: 2026-11-13-scripted-example-record-a-showcase-run-001
  storage:      /Users/robertdevore/2026/Kujolang/kujo-repos/howl/campaign/evidence/verified/runledger/artifacts/ledger/runs/2026-11-13-scripted-example-record-a-showcase-run-001.json
  repo:         /Users/robertdevore/2026/Kujolang/kujo-repos/howl/campaign/..
  start commit: 769af8827ab7f32e3b5f009d50f7643a45144fea

Next: runledger finish 2026-11-13-scripted-example-record-a-showcase-run-001 --status <pass|partial|fail|abandoned> --verdict "..."
Finished run: 2026-11-13-scripted-example-record-a-showcase-run-001
  status:       pass
  end commit:   769af8827ab7f32e3b5f009d50f7643a45144fea
  changed files: 88
Wrote report to /Users/robertdevore/2026/Kujolang/kujo-repos/howl/campaign/evidence/verified/runledger/artifacts/report.md
{
  "errors": [],
  "valid": 1
}
```

**Concepts:** Verified with Kujo

An agent session ends, and its run context disappears into chat history. Executed a scripted receipt lifecycle using provider local and model scripted-example. Pass is a supplied demonstration verdict. No token usage, costs, model invocation, or automated quality judgment is claimed. Output shown here, when present, was observed in evidence/verified/runledger/stdout.txt. Full commands and artifacts are in the verification report.

---

Agent work should leave something useful after the chat closes. With RunLedger I can start a run, record how it finished, and write a report. The receipt stays in the repo workflow, ready for the next person picking up the work.

https://github.com/kujolang/runledger/blob/ab0ec5d2edb7ffd913f48d092aa6fc17cab58d13/README.md#quick-start

Kujo: Real examples. Recorded execution. Clear limits.
