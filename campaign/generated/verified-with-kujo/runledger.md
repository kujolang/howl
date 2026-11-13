# RunLedger

Keep a run receipt after the chat ends.

```bash
runledger finish "$id" \
  --status pass --verdict "Ready for review"

runledger report --output run-report.md
runledger verify --json

```

**Expected output:**

```text
Finished run: 2026-11-13-demo-showcase-receipt-001
  status:       pass
  end commit:   -
  changed files: 0
Wrote report to run-report.md
{
  "errors": [],
  "valid": 1
}
```

**Concepts:** Verified with Kujo

An agent session ends, and its run context disappears into chat history. Executed a scripted receipt lifecycle using provider local and model scripted-example. Pass is a supplied demonstration verdict. No token usage, costs, model invocation, or automated quality judgment is claimed. Set id to the run ID printed by runledger start, then run from the directory containing its ledger. Output shown here, when present, was observed in evidence/tool-commands/runledger/stdout.txt. Full commands and artifacts are in the verification report.

---

Agent work should leave something useful after the chat closes. With RunLedger I can start a run, record how it finished, and write a report. The receipt stays in the repo workflow, ready for the next person picking up the work.

https://github.com/kujolang/runledger/blob/ab0ec5d2edb7ffd913f48d092aa6fc17cab58d13/README.md#quick-start

Verified with Kujo: Real examples. Recorded execution. Clear limits.
