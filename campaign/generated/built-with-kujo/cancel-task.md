# Stop a task

Stop cooperative work; handle rejection.

```kujo
shared_set("started", false)
func work() {
    shared_set("started", true)
    loop {}
}
handle := spawn_task(work)
while shared_get("started") == false {}
print(cancel_task(handle))
try { await await_task(handle) }
except err { print("cancelled") }

```

**Expected output:**

```text
true
cancelled
```

**Concepts:** Built with Kujo

A background task needs a deliberate stop path. Reduced the lifecycle cancellation contract. The shared started flag prevents a start/cancel race. Cancellation is cooperative; this does not promise interruption of arbitrary blocking native calls. Output shown here, when present, was observed in evidence/verified/cancel-task/stdout.txt. Full commands and artifacts are in the verification report.

---

Background work needs a stop path. This Kujo example waits until a task starts, cancels it, and handles the rejected await. It demonstrates cooperative cancellation, not a magic undo button for side effects.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/tests/concurrency&#95;lifecycle&#95;contracts.rs

Built with Kujo: Real examples. Recorded execution. Clear limits.
