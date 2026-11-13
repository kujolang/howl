# PackWrite

Offline pack checks. No model call.

```bash
#!/usr/bin/env bash
set -euo pipefail
"$RELEASES/packwrite-source/bin/packwrite" validate \
  --output agent --config packwrite.toml --json
"$RELEASES/packwrite-source/bin/packwrite" summary \
  --output agent --config packwrite.toml --json

```

**Expected output:**

```text
{"errors":[],"ok":true,"warnings":[]}
{"errors":[],"missing_files":[],"next_command":"packwrite prompt deepseek","ok":true,"output_dir":"agent","phase_count":6,"warnings":[]}
```

**Concepts:** Verified with Kujo

An incomplete agent pack can send the next session into guesswork. Executed validate and summary on the released golden-agent fixture with six phases. The fixture is a test input, not newly generated model output. No provider was called. Output shown here, when present, was observed in evidence/verified/packwrite/stdout.txt. Full commands and artifacts are in the verification report.

---

An agent handoff is only useful if the pieces are there. Here PackWrite validates an existing six-phase fixture and reports no missing files. This is the offline validation path, not a claim about a freshly generated plan.

https://github.com/kujolang/packwrite/blob/721dcc0ad41eaedc159d84f34a06396f92ede79f/README.md#commands

Verified with Kujo: Real examples. Recorded execution. Clear limits.
