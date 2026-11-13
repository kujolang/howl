# Safer output

Redact secrets in print and JSON output.

```kujo
api_key := secret("sk-local-demo")
print(api_key)
print(to_json({"api_key": api_key}))
print(is_secret(api_key))

```

**Expected output:**

```text
***
{"api_key":"***"}
true
```

**Concepts:** Built with Kujo

A debug print can accidentally disclose a credential. Reduced the canonical secret example; the dummy value is not a credential. Redaction is not encryption and explicit reveal remains possible. Output shown here, when present, was observed in evidence/verified/secret-output/stdout.txt. Full commands and artifacts are in the verification report.

---

I still use print to debug things. Kujo lets me wrap a value with secret() so it shows up as &#42;&#42;&#42; in terminal output and JSON. Here is the whole example. A useful default for values you do not want wandering into logs.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/secrets&#95;redaction.kujo

Built with Kujo: Real examples. Recorded execution. Clear limits.
