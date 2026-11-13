# X drafts

Not published. Links point to pinned source. Each draft fits 280 characters with X URL weighting (23 characters per URL).

## Built with Kujo — Bounded work

I like being able to put a limit right next to the work. In Kujo, parallel_map takes the inputs, a function, and a concurrency limit. Here it doubles four values with at most two jobs at a time. Await it and get the results back in order.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/test_parallel_simple.kujo

## Built with Kujo — Read it twice

Run the task once. Read the result wherever you need it. Kujo lets you await the same task handle more than once, so a second reader gets the completed result too. Six lines that make task coordination a little less annoying.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/tests/language_task_contracts.rs

## Built with Kujo — Stop a task

Start a task, wait until it is running, cancel it, handle the result. This is what cooperative task cancellation looks like in Kujo. The stop path lives right alongside the work, where the next developer can actually find it.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/tests/concurrency_lifecycle_contracts.rs

## Built with Kujo — Stable JSON

Same data, different key order, identical JSON. Kujo sorts dictionary keys when it serializes them, including nested dictionaries. Handy when you want generated files to produce useful diffs instead of rearranging themselves every run.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/helper_hlp_015_canonical_json.kujo

## Built with Kujo — Read the exit

Running commands from code gets easier when the result has fields. Kujo gives you stdout, exit status, timeout, and truncation flags. Here I run a command and check the result directly. Small thing, but useful in an agent tool loop.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/helper_hlp_013_process_result.kujo

## Built with Kujo — Safer output

I still use print to debug things. Kujo lets me wrap a value with secret() so it shows up as *** in terminal output and JSON. Here is the whole example. A useful default for values you do not want wandering into logs.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/secrets_redaction.kujo

## Verified with Kujo — Eval

Here is a small Eval suite you can actually run: check that a command succeeds, that a manifest exists, and that the file clears a size check. Three explicit checks, with JSON results ready for the next step in your workflow.

https://github.com/kujolang/eval/blob/71e66dff780d6930bcbe093c046bf31aa26411df/examples/release_gate_suite.json

## Verified with Kujo — Workcell

I want to review the settings before agent work starts. Workcell can show the resolved network policy, filesystem settings, and resource limits from one definition. This example uses inspect to make that preflight easy to read.

https://github.com/kujolang/workcell/blob/189d7ab6e975301a0e5100b65e8ad3fe4a584573/examples/hello/workcell.json

## Verified with Kujo — PackWrite

Before handing a pack to the next agent, check that it is complete. PackWrite validates the files and reports the phase count and anything missing. This six-phase sample is a quick way to try the workflow locally.

https://github.com/kujolang/packwrite/blob/721dcc0ad41eaedc159d84f34a06396f92ede79f/README.md#commands

## Verified with Kujo — RunLedger

Agent work should leave something useful after the chat closes. With RunLedger I can start a run, record how it finished, and write a report. The receipt stays in the repo workflow, ready for the next person picking up the work.

https://github.com/kujolang/runledger/blob/ab0ec5d2edb7ffd913f48d092aa6fc17cab58d13/README.md#quick-start

## Verified with Kujo — Lens

Built a page? Give the next developer more than a screenshot from your laptop. This Lens example checks a local dashboard at desktop and mobile sizes and saves screenshots, browser findings, and a report they can inspect.

https://github.com/kujolang/lens/blob/85778065ca329c93293b387a0e7011437b6d0c60/examples/specs/dashboard.json

## Verified with Kujo — ShipCheck

I would rather put the release checklist in a command than keep it in my head. ShipCheck looks for the repo signals I need before shipping and gives me JSON plus a gate exit code. Here is the small example to try in a local checkout.

https://github.com/kujolang/shipcheck/blob/7eedd9e02d8730d65e06e16f4984d909d23539bc/README.md#gate-semantics
