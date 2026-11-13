# Lens

Check desktop and mobile; keep evidence.

```bash
./lens check http://127.0.0.1:3000/dashboard/ \
  --spec dashboard.json \
  --html --accessibility --check-links \
  --out lens-results

```

**Expected output:**

```text
Lens completed: PASS
Report: lens-results/lens-report.md
```

**Concepts:** Verified with Kujo

A page can look fine at one size and still have console or layout problems. Executed a local dashboard fixture with desktop/mobile screenshots, accessibility and link checks. Adapted the canonical spec by removing unsupported not&#95;exists. No accessibility certification or production-site coverage is claimed. Run from a Lens checkout with dashboard.json present and the dashboard served locally on port 3000. Output shown here, when present, was observed in evidence/tool-commands/lens/stdout.txt. Full commands and artifacts are in the verification report.

---

Built a page? Give the next developer more than a screenshot from your laptop. This Lens example checks a local dashboard at desktop and mobile sizes and saves screenshots, browser findings, and a report they can inspect.

https://github.com/kujolang/lens/blob/85778065ca329c93293b387a0e7011437b6d0c60/examples/specs/dashboard.json

Kujo: Real examples. Recorded execution. Clear limits.
