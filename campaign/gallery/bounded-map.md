# Bounded work

Limit concurrent batch work to two jobs.

```kujo
items := [1, 2, 3, 4]
pending := parallel_map(items, func(x) {
    return x * 2
}, 2)
print(to_json(await pending))

```

**Expected output:**

```text
[2,4,6,8]
```

**Concepts:** Built with Kujo

A batch of jobs should not turn into an unbounded pile of work. Reduced the canonical parallel&#95;map example to four inputs and a limit of two. This verifies results and ordering, not a speedup. Output shown here, when present, was observed in evidence/verified/bounded-map/stdout.txt. Full commands and artifacts are in the verification report.

---

I like being able to put a limit right next to the work. In Kujo, parallel&#95;map takes the inputs, a function, and a concurrency limit. Here it doubles four values with at most two jobs at a time. Await it and get the results back in order.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/test&#95;parallel&#95;simple.kujo

Kujo: Real examples. Recorded execution. Clear limits.
