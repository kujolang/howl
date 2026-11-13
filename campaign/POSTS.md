# X drafts

Not published. Links point to pinned source. Each draft fits 280 characters with X URL weighting (23 characters per URL).

## Built with Kujo — Bounded work

I want batch work to have a ceiling. This Kujo example maps four inputs with a concurrency limit of two, then awaits the results. Small enough to read at a glance. No speedup claim, just an explicit limit.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/test_parallel_simple.kujo

## Built with Kujo — Read it twice

A task result should not disappear because something already waited for it. This Kujo example awaits the same task twice and gets the same value. Cancelling it after completion returns false. Useful behavior to make explicit.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/tests/language_task_contracts.rs

## Built with Kujo — Stop a task

Background work needs a stop path. This Kujo example waits until a task starts, cancels it, and handles the rejected await. It demonstrates cooperative cancellation, not a magic undo button for side effects.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/tests/concurrency_lifecycle_contracts.rs

## Built with Kujo — Stable JSON

Noisy JSON diffs waste review time. Kujo serializes these nested dictionaries identically even though the keys were inserted in a different order. Tiny example, useful property for files that people and tools both read.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/helper_hlp_015_canonical_json.kujo

## Built with Kujo — Read the exit

When an agent runs a command, I want more than a blob of terminal text. This Kujo example checks success and exit status, then reads stdout, timeout, and truncation fields directly. No parsing a status message.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/helper_hlp_013_process_result.kujo

## Built with Kujo — Safer output

A debug print should not casually dump a secret. Wrapping this dummy value with secret() makes Kujo redact it in both print and JSON output. This example checks those boundaries; it does not claim encryption.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/secrets_redaction.kujo

## Verified with Kujo — Eval

“It ran” is a weak handoff. This Eval example runs the canonical release smoke suite: a command succeeds, the manifest exists, and its size clears the check. The JSON results stay available for the next tool or reviewer.

https://github.com/kujolang/eval/blob/71e66dff780d6930bcbe093c046bf31aa26411df/examples/release_gate_suite.json

## Verified with Kujo — Workcell

Before running agent work, I want to see the boundaries. Workcell resolves this hello definition into a compact policy summary: network off, read-only root, explicit limits. This card verifies preflight; it does not claim a container ran.

https://github.com/kujolang/workcell/blob/189d7ab6e975301a0e5100b65e8ad3fe4a584573/examples/hello/workcell.json

## Verified with Kujo — PackWrite

An agent handoff is only useful if the pieces are there. Here PackWrite validates an existing six-phase fixture and reports no missing files. This is the offline validation path, not a claim about a freshly generated plan.

https://github.com/kujolang/packwrite/blob/721dcc0ad41eaedc159d84f34a06396f92ede79f/README.md#commands

## Verified with Kujo — RunLedger

I do not want run history trapped in chat. This RunLedger example starts a local receipt, finishes it, writes a report, and checks the ledger. The verdict is supplied by the caller. Token usage and costs stay unset.

https://github.com/kujolang/runledger/blob/ab0ec5d2edb7ffd913f48d092aa6fc17cab58d13/README.md#quick-start

## Verified with Kujo — Lens

“Looks fine here” is not much evidence. Lens checked this local dashboard at desktop and mobile sizes, applied the supported spec assertions, and saved screenshots plus reports. Useful handoff material without an LLM judging the page.

https://github.com/kujolang/lens/blob/85778065ca329c93293b387a0e7011437b6d0c60/examples/specs/dashboard.json

## Verified with Kujo — ShipCheck

Release prep should not depend on remembering every file. ShipCheck gates this pinned repo checkout on its readiness checks and returns JSON plus an exit code. It checks release signals; it does not run the project tests for you.

https://github.com/kujolang/shipcheck/blob/7eedd9e02d8730d65e06e16f4984d909d23539bc/README.md#gate-semantics
