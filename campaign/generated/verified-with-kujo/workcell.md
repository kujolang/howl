# Workcell

Review execution policy before work starts.

```bash
#!/usr/bin/env bash
set -euo pipefail
"$RELEASES/workcell-source/bin/workcell" validate \
  --file "$CAMPAIGN/inputs/workcell.json"
"$RELEASES/workcell-source/bin/workcell" inspect \
  --file "$CAMPAIGN/inputs/workcell.json" \
  --repo "$CAMPAIGN/.." --summary

```

**Expected output:**

```text
Valid Workcell definition: /Users/robertdevore/2026/Kujolang/kujo-repos/howl/campaign/inputs/workcell.json
Name: hello-workcell  Backend: docker  Network: none
{"backend":{"adapter_id":"docker","provider_id":"docker","substrate":"oci"},"definition":{"name":"hello-workcell","schema":"workcell-definition/v1"},"error":"","ok":true,"policy":{"cpus":1,"memory":"256m","network":"none","pids":64,"read_only_root":true,"timeout_ms":60000},"schema_version":"workcell-inspect-summary/v1"}
```

**Concepts:** Verified with Kujo

Execution settings are hard to review when they are buried in launch commands. Executed validate and inspect --summary on the unchanged hello definition. No container was launched; Docker was unavailable. Network none and resource limits are resolved policy, not observed enforcement. Output shown here, when present, was observed in evidence/verified/workcell/stdout.txt. Full commands and artifacts are in the verification report.

---

I want to review the settings before agent work starts. Workcell can show the resolved network policy, filesystem settings, and resource limits from one definition. This example uses inspect to make that preflight easy to read.

https://github.com/kujolang/workcell/blob/189d7ab6e975301a0e5100b65e8ad3fe4a584573/examples/hello/workcell.json

Verified with Kujo: Real examples. Recorded execution. Clear limits.
