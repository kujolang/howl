# Verification report

Verified November 12, 2026 (America/Detroit). Machine receipts retain UTC timestamps, which cross into November 13.

**12/12 examples executed successfully within the scopes below.** No example is being represented as unexecuted successful work. Each success requires exit 0 and campaign assertions. These results are not a claim that every capability of each tool was tested.

Runtime: downloaded Kujo 1.9.0 macOS x64 release binary. Its archive SHA-256 matched the official release checksum. Exact archive/binary hashes and all tool release commits are in [releases.json](releases.json). Latest published release tags were checked through GitHub releases/latest and local tags matched remote tag commit IDs. Source execution uses those release snapshots, not newer working-tree builds.

| Example | Executed scope | Exit | Evidence |
| --- | --- | ---: | --- |
| Built with Kujo: Bounded work | parallel_map with limit 2; exact ordered JSON result | 0 | [Receipt](evidence/verified/bounded-map/receipt.json), [stdout](evidence/verified/bounded-map/stdout.txt), [expanded commands / stderr](evidence/verified/bounded-map/stderr.txt) |
| Built with Kujo: Read it twice | Two waits return 21; cancelling completed work returns false | 0 | [Receipt](evidence/verified/reusable-task/receipt.json), [stdout](evidence/verified/reusable-task/stdout.txt), [expanded commands / stderr](evidence/verified/reusable-task/stderr.txt) |
| Built with Kujo: Stop a task | Started task cancels; awaiting rejects and is handled | 0 | [Receipt](evidence/verified/cancel-task/receipt.json), [stdout](evidence/verified/cancel-task/stdout.txt), [expanded commands / stderr](evidence/verified/cancel-task/stderr.txt) |
| Built with Kujo: Stable JSON | Nested dictionaries serialize identically | 0 | [Receipt](evidence/verified/canonical-json/receipt.json), [stdout](evidence/verified/canonical-json/stdout.txt), [expanded commands / stderr](evidence/verified/canonical-json/stderr.txt) |
| Built with Kujo: Read the exit | printf success, exitcode, stdout, timeout, truncation fields | 0 | [Receipt](evidence/verified/process-result/receipt.json), [stdout](evidence/verified/process-result/stdout.txt), [expanded commands / stderr](evidence/verified/process-result/stderr.txt) |
| Built with Kujo: Safer output | Dummy secret redacts in print and JSON | 0 | [Receipt](evidence/verified/secret-output/receipt.json), [stdout](evidence/verified/secret-output/stdout.txt), [expanded commands / stderr](evidence/verified/secret-output/stderr.txt) |
| Verified with Kujo: Eval | Canonical release suite: 3 passed, 0 failed | 0 | [Receipt](evidence/verified/eval/receipt.json), [stdout](evidence/verified/eval/stdout.txt), [expanded commands / stderr](evidence/verified/eval/stderr.txt) |
| Verified with Kujo: Workcell | validate + inspect --summary; resolved policy only | 0 | [Receipt](evidence/verified/workcell/receipt.json), [stdout](evidence/verified/workcell/stdout.txt), [expanded commands / stderr](evidence/verified/workcell/stderr.txt) |
| Verified with Kujo: PackWrite | validate + summary of six-phase released fixture | 0 | [Receipt](evidence/verified/packwrite/receipt.json), [stdout](evidence/verified/packwrite/stdout.txt), [expanded commands / stderr](evidence/verified/packwrite/stderr.txt) |
| Verified with Kujo: RunLedger | start → finish → report → verify; one valid receipt | 0 | [Receipt](evidence/verified/runledger/receipt.json), [stdout](evidence/verified/runledger/stdout.txt), [expanded commands / stderr](evidence/verified/runledger/stderr.txt) |
| Verified with Kujo: Lens | Desktop/mobile browser check, supported spec, links, axe | 0 | [Receipt](evidence/verified/lens/receipt.json), [stdout](evidence/verified/lens/stdout.txt), [expanded commands / stderr](evidence/verified/lens/stderr.txt) |
| Verified with Kujo: ShipCheck | gate against pinned ShipCheck source: exit 0 | 0 | [Receipt](evidence/verified/shipcheck/receipt.json), [stdout](evidence/verified/shipcheck/stdout.txt), [expanded commands / stderr](evidence/verified/shipcheck/stderr.txt) |

## Exact commands, source and boundaries

Each receipt records the actual argument vector, working directory, source SHA-256, runtime version, allowlisted environment paths, exit code, and generated-artifact hashes. Shell traces retain expanded inner commands. `results.json` indexes all twelve. Output was captured from execution; README expected-output examples were not used as observations. The runner creates temporary working directories, which are intentionally removed.

### bounded-map

**Problem:** A batch of jobs should not turn into an unbounded pile of work.

**Source:** [kujo pinned upstream](https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/test_parallel_simple.kujo). Local executable: [examples/bounded-map.kujo](examples/bounded-map.kujo).

**Observed scope:** Reduced the canonical parallel_map example to four inputs and a limit of two. This verifies results and ordering, not a speedup.

**Artifacts:** No tool-generated files; stdout, stderr, and the campaign execution receipt were retained.

### reusable-task

**Problem:** Reading a completed task once should not consume its result.

**Source:** [kujo pinned upstream](https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/tests/language_task_contracts.rs). Local executable: [examples/reusable-task.kujo](examples/reusable-task.kujo).

**Observed scope:** Extracted the reusable-completion contract into a standalone example. Both waits return 21; cancelling the completed task returns false.

**Artifacts:** No tool-generated files; stdout, stderr, and the campaign execution receipt were retained.

### cancel-task

**Problem:** A background task needs a deliberate stop path.

**Source:** [kujo pinned upstream](https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/tests/concurrency_lifecycle_contracts.rs). Local executable: [examples/cancel-task.kujo](examples/cancel-task.kujo).

**Observed scope:** Reduced the lifecycle cancellation contract. The shared started flag prevents a start/cancel race. Cancellation is cooperative; this does not promise interruption of arbitrary blocking native calls.

**Artifacts:** No tool-generated files; stdout, stderr, and the campaign execution receipt were retained.

### canonical-json

**Problem:** Dictionary insertion order creates noisy diffs and unstable machine output.

**Source:** [kujo pinned upstream](https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/helper_hlp_015_canonical_json.kujo). Local executable: [examples/canonical-json.kujo](examples/canonical-json.kujo).

**Observed scope:** Reduced the canonical HLP-015 example to nested key ordering and equality.

**Artifacts:** No tool-generated files; stdout, stderr, and the campaign execution receipt were retained.

### process-result

**Problem:** Shell text alone does not tell an agent whether a process timed out or failed.

**Source:** [kujo pinned upstream](https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/helper_hlp_013_process_result.kujo). Local executable: [examples/process-result.kujo](examples/process-result.kujo).

**Observed scope:** Adapted HLP-013 from rustc --version to a portable printf command. Checks success and exitcode, then prints structured output, timeout and truncation flags.

**Artifacts:** No tool-generated files; stdout, stderr, and the campaign execution receipt were retained.

### secret-output

**Problem:** A debug print can accidentally disclose a credential.

**Source:** [kujo pinned upstream](https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/secrets_redaction.kujo). Local executable: [examples/secret-output.kujo](examples/secret-output.kujo).

**Observed scope:** Reduced the canonical secret example; the dummy value is not a credential. Redaction is not encryption and explicit reveal remains possible.

**Artifacts:** No tool-generated files; stdout, stderr, and the campaign execution receipt were retained.

### eval

**Problem:** A successful command alone is not a complete release smoke check.

**Source:** [eval pinned upstream](https://github.com/kujolang/eval/blob/71e66dff780d6930bcbe093c046bf31aa26411df/examples/release_gate_suite.json). Local executable: [examples/eval.sh](examples/eval.sh).

**Observed scope:** Executed the unchanged canonical three-check release suite against its copied kennel.toml fixture. This checks a command, file existence, and file size; it does not evaluate model quality.

**Artifacts:** [`artifacts/artifact-manifest.json`](evidence/verified/eval/artifacts/artifact-manifest.json); [`artifacts/badge.json`](evidence/verified/eval/artifacts/badge.json); [`artifacts/cli-summary.json`](evidence/verified/eval/artifacts/cli-summary.json); [`artifacts/eval-report.md`](evidence/verified/eval/artifacts/eval-report.md); [`artifacts/eval-report.md.cache.json`](evidence/verified/eval/artifacts/eval-report.md.cache.json); [`artifacts/evaluation-result.json`](evidence/verified/eval/artifacts/evaluation-result.json); [`artifacts/history.json`](evidence/verified/eval/artifacts/history.json); [`artifacts/last_failures.json`](evidence/verified/eval/artifacts/last_failures.json); [`artifacts/last_run.json`](evidence/verified/eval/artifacts/last_run.json); [`artifacts/summary.json`](evidence/verified/eval/artifacts/summary.json)

### workcell

**Problem:** Execution settings are hard to review when they are buried in launch commands.

**Source:** [workcell pinned upstream](https://github.com/kujolang/workcell/blob/189d7ab6e975301a0e5100b65e8ad3fe4a584573/examples/hello/workcell.json). Local executable: [examples/workcell.sh](examples/workcell.sh).

**Observed scope:** Executed validate and inspect --summary on the unchanged hello definition. No container was launched; Docker was unavailable. Network none and resource limits are resolved policy, not observed enforcement.

**Artifacts:** No tool-generated files; stdout, stderr, and the campaign execution receipt were retained.

### packwrite

**Problem:** An incomplete agent pack can send the next session into guesswork.

**Source:** [packwrite pinned upstream](https://github.com/kujolang/packwrite/blob/721dcc0ad41eaedc159d84f34a06396f92ede79f/README.md#commands). Local executable: [examples/packwrite.sh](examples/packwrite.sh).

**Observed scope:** Executed validate and summary on the released golden-agent fixture with six phases. The fixture is a test input, not newly generated model output. No provider was called.

**Artifacts:** [`artifacts/validated-pack/CODEX_REVIEW_PROMPT.md`](evidence/verified/packwrite/artifacts/validated-pack/CODEX_REVIEW_PROMPT.md); [`artifacts/validated-pack/DECISIONS.md`](evidence/verified/packwrite/artifacts/validated-pack/DECISIONS.md); [`artifacts/validated-pack/DEEPSEEK_START.md`](evidence/verified/packwrite/artifacts/validated-pack/DEEPSEEK_START.md); [`artifacts/validated-pack/HANDOFF.md`](evidence/verified/packwrite/artifacts/validated-pack/HANDOFF.md); [`artifacts/validated-pack/MASTER.md`](evidence/verified/packwrite/artifacts/validated-pack/MASTER.md); [`artifacts/validated-pack/REVIEW_CHECKLIST.md`](evidence/verified/packwrite/artifacts/validated-pack/REVIEW_CHECKLIST.md); [`artifacts/validated-pack/TODO.md`](evidence/verified/packwrite/artifacts/validated-pack/TODO.md); [`artifacts/validated-pack/phases/00-project-brief.md`](evidence/verified/packwrite/artifacts/validated-pack/phases/00-project-brief.md); [`artifacts/validated-pack/phases/01-alpha.md`](evidence/verified/packwrite/artifacts/validated-pack/phases/01-alpha.md); [`artifacts/validated-pack/phases/02-beta.md`](evidence/verified/packwrite/artifacts/validated-pack/phases/02-beta.md); [`artifacts/validated-pack/phases/03-gamma.md`](evidence/verified/packwrite/artifacts/validated-pack/phases/03-gamma.md); [`artifacts/validated-pack/phases/04-delta.md`](evidence/verified/packwrite/artifacts/validated-pack/phases/04-delta.md); [`artifacts/validated-pack/phases/05-epsilon.md`](evidence/verified/packwrite/artifacts/validated-pack/phases/05-epsilon.md)

### runledger

**Problem:** An agent session ends, and its run context disappears into chat history.

**Source:** [runledger pinned upstream](https://github.com/kujolang/runledger/blob/ab0ec5d2edb7ffd913f48d092aa6fc17cab58d13/README.md#quick-start). Local executable: [examples/runledger.sh](examples/runledger.sh).

**Observed scope:** Executed a scripted receipt lifecycle using provider local and model scripted-example. Pass is a supplied demonstration verdict. No token usage, costs, model invocation, or automated quality judgment is claimed.

**Artifacts:** [`artifacts/ledger/runs/2026-11-13-scripted-example-record-a-showcase-run-001.json`](evidence/verified/runledger/artifacts/ledger/runs/2026-11-13-scripted-example-record-a-showcase-run-001.json); [`artifacts/report.md`](evidence/verified/runledger/artifacts/report.md)

### lens

**Problem:** A page can look fine at one size and still have console or layout problems.

**Source:** [lens pinned upstream](https://github.com/kujolang/lens/blob/85778065ca329c93293b387a0e7011437b6d0c60/examples/specs/dashboard.json). Local executable: [examples/lens.sh](examples/lens.sh).

**Observed scope:** Executed a local dashboard fixture with desktop/mobile screenshots, accessibility and link checks. Adapted the canonical spec by removing unsupported not_exists. No accessibility certification or production-site coverage is claimed.

**Artifacts:** [`artifacts/accessibility.json`](evidence/verified/lens/artifacts/accessibility.json); [`artifacts/console.json`](evidence/verified/lens/artifacts/console.json); [`artifacts/dom-summary.json`](evidence/verified/lens/artifacts/dom-summary.json); [`artifacts/lens-report.html`](evidence/verified/lens/artifacts/lens-report.html); [`artifacts/lens-report.json`](evidence/verified/lens/artifacts/lens-report.json); [`artifacts/lens-report.md`](evidence/verified/lens/artifacts/lens-report.md); [`artifacts/links.json`](evidence/verified/lens/artifacts/links.json); [`artifacts/metadata.json`](evidence/verified/lens/artifacts/metadata.json); [`artifacts/network.json`](evidence/verified/lens/artifacts/network.json); [`artifacts/screenshots/desktop.png`](evidence/verified/lens/artifacts/screenshots/desktop.png); [`artifacts/screenshots/mobile.png`](evidence/verified/lens/artifacts/screenshots/mobile.png)

### shipcheck

**Problem:** A release checklist is easy to forget when shipping gets busy.

**Source:** [shipcheck pinned upstream](https://github.com/kujolang/shipcheck/blob/7eedd9e02d8730d65e06e16f4984d909d23539bc/README.md#gate-semantics). Local executable: [examples/shipcheck.sh](examples/shipcheck.sh).

**Observed scope:** Executed gate --format json against the pinned ShipCheck release checkout. This checks repository readiness signals, not test execution, artifact integrity, or release certification.

**Artifacts:** [`artifacts/scan.json`](evidence/verified/shipcheck/artifacts/scan.json)

## Limits that matter

- Workcell: Docker daemon was unavailable. The chosen example is a successful, executable **preflight**, not container execution or enforcement verification. No hello.txt container artifact is claimed.
- PackWrite: validation of the released golden fixture, not provider generation. Copied fixture files are labeled validated-pack, not generated pack.
- RunLedger: the supplied pass verdict describes this scripted lifecycle only. Unknown usage/cost fields remain unset. Its timestamp and dirty-tree facts describe the actual run before campaign commits.
- Lens: local authored dashboard only. The canonical unsupported not_exists assertion was removed; links were enabled. Final evidence reports 0 skipped checks and 0 automated accessibility violations. This is not WCAG certification.
- ShipCheck: command is `kujo run shipcheck.kujo gate --dir <pinned ShipCheck checkout> --format json`. Exit 0; summary: `{"failed_errors": 0, "gate_passed": 1, "passed": 16, "total_checks": 16, "warnings": 0}`. No error/warning findings; only informational passing checks. It does not execute project tests.
- Cancellation: cooperative checkpoints only; arbitrary blocking native effects are not proven interruptible. No performance or resource-use benchmark was run.

## Rendering and publication verification

The [render receipt](evidence/render.json) captures successful validation/render commands for all three Howl manifests. `generated/` preserves unmodified SVG/HTML/Markdown/galleries; `gallery/` contains the branded publication copies and twelve 1200×630 PNG conversions. The final artifact audit is [evidence/artifact-audit.json](evidence/artifact-audit.json).

SVG and Markdown publication copies are identical to released Howl output. HTML changes are campaign CSS, navigation, and previews only. No Howl application, renderer, tests, existing examples, or root manifest was changed.

Howl regression check: `KUJO=/tmp/howl-campaign-releases/kujo ./tests/run.sh` exited 0 with 106 assertions passing, plus containment/filesystem/CLI hardening checks. All six added `.kujo` files pass `kujo check`; see [language-checks.json](evidence/language-checks.json). A second render was compared by SHA-256 for every generated/publication file; see [regeneration.json](evidence/regeneration.json).
