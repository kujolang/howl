# Read the exit

Read exit status without parsing text.

```kujo
result := spawn_process(["printf", "ready"],
    {"max_output_bytes": 4096})
assert(result.success == true)
assert(result.exitcode == 0)
print(result.stdout)
print(result.timed_out)
print(result.stdout_truncated)

```

**Expected output:**

```text
ready
false
false
```

**Concepts:** Built with Kujo

Shell text alone does not tell an agent whether a process timed out or failed. Adapted HLP-013 from rustc --version to a portable printf command. Checks success and exitcode, then prints structured output, timeout and truncation flags. Output shown here, when present, was observed in evidence/verified/process-result/stdout.txt. Full commands and artifacts are in the verification report.

---

Running commands from code gets easier when the result has fields. Kujo gives you stdout, exit status, timeout, and truncation flags. Here I run a command and check the result directly. Small thing, but useful in an agent tool loop.

https://github.com/kujolang/kujo/blob/2cfaf185ad03059c89ef4f72fb061074255d00fc/examples/helper&#95;hlp&#95;013&#95;process&#95;result.kujo

Built with Kujo: Real examples. Recorded execution. Clear limits.
