# Read it twice

Await the same task result more than once.

```kujo
func work() { return 21 }
handle := spawn_task(work)
first := await await_task(handle)
second := await await_task(handle)
print(first + second)
print(cancel_task(handle))

```

**Expected output:**

```text
42
false
```

**Concepts:** Built with Kujo

Reading a completed task once should not consume its result. Extracted the reusable-completion contract into a standalone example. Both waits return 21; cancelling the completed task returns false. Output shown here, when present, was observed in evidence/verified/reusable-task/stdout.txt. Full commands and artifacts are in the verification report.

---

A task result should not disappear because something already waited for it. This Kujo example awaits the same task twice and gets the same value. Cancelling it after completion returns false. Useful behavior to make explicit.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/tests/language&#95;task&#95;contracts.rs

Kujo: Real examples. Recorded execution. Clear limits.
