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

A debug print should not casually dump a secret. Wrapping this dummy value with secret() makes Kujo redact it in both print and JSON output. This example checks those boundaries; it does not claim encryption.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/secrets&#95;redaction.kujo

Built with Kujo: Real examples. Recorded execution. Clear limits.
