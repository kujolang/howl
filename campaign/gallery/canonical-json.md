# Stable JSON

Stable JSON, even when key order changes.

```kujo
first := {"z": 1, "a": {"b": 2, "a": 1}}
second := {"a": {"a": 1, "b": 2}, "z": 1}
print(to_json(first))
print(to_json(first) == to_json(second))

```

**Expected output:**

```text
{"a":{"a":1,"b":2},"z":1}
true
```

**Concepts:** Built with Kujo

Dictionary insertion order creates noisy diffs and unstable machine output. Reduced the canonical HLP-015 example to nested key ordering and equality. Output shown here, when present, was observed in evidence/verified/canonical-json/stdout.txt. Full commands and artifacts are in the verification report.

---

Noisy JSON diffs waste review time. Kujo serializes these nested dictionaries identically even though the keys were inserted in a different order. Tiny example, useful property for files that people and tools both read.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/helper&#95;hlp&#95;015&#95;canonical&#95;json.kujo

Kujo: Real examples. Recorded execution. Clear limits.
