# Howl next-session review - 2026-06-19

This note captures the remaining improvement opportunities after the June 19
hardening pass. Howl is stable and production-ready for its intended offline
showcase-artifact scope; the items below are incremental ways to make it more
polished, more broadly useful, and an even stronger demonstration of Kujo.

## Completed in this pass

- Hardened CLI option parsing so missing option values, unknown flags, invalid
  render formats, invalid caption platforms, and non-positive line limits fail
  with clear `howl:` errors before any work starts.
- Added output-directory safety checks for render output. Blank, root, current
  directory, traversal, and ambiguous paths are rejected before writes happen.
- Tightened manifest validation for top-level shape, required field types,
  optional string fields, `project`, `theme`, and `concepts`.
- Hardened Markdown rendering by escaping manifest prose and switching code
  fence markers when example code contains backticks.
- Removed stale `tests/howl_test.out`, which recorded an old failing run and
  was no longer part of the harness.
- Updated README positioning and security notes to describe Howl as
  production-ready within scope, not as a broad enterprise platform.
- Expanded tests from 58 to 70 assertions plus shell-level CLI failure
  contracts.

## Next high-value improvements

1. Add optional dark theme rendering.
   - Keep it deterministic and offline.
   - Use the existing `theme.mode` and card `variant` fields rather than adding
     a plugin system.
   - Add HTML/SVG snapshot-style tests for light and dark output markers.

2. Improve `howl init --manifest nested/path/howl.json`.
   - Create starter examples relative to the manifest directory.
   - Ensure parent directories are created predictably.
   - Add CLI contract tests for default and nested init paths.

3. Add a machine-readable validation mode.
   - Candidate command shape: `howl validate --json`.
   - Return stable JSON with `ok`, `problems`, `cards`, and manifest path.
   - Keep the current human-readable output as the default.

4. Add a dry-run render mode.
   - Candidate command shape: `howl render --dry-run`.
   - Report the exact files that would be written without touching the
     filesystem.
   - Useful for CI, docs pipelines, and agent review.

5. Add committed artifact drift helpers.
   - Candidate command shape: `howl render --check`.
   - Compare generated output against existing files and exit non-zero on drift.
   - If Kujo lacks enough filesystem diff primitives, document a shell recipe
     instead of forcing a brittle in-language implementation.

6. Add stricter optional URL handling.
   - Treat `url` as display-only today.
   - Consider accepting only empty, relative, `http://`, or `https://` URLs.
   - Reject `javascript:` and other surprising schemes before rendering links.

7. Expand hostile-content tests.
   - Include Markdown notes/captions containing raw HTML.
   - Include project names and concepts containing HTML-sensitive characters.
   - Include example code containing both backtick and tilde fences.

8. Add a compact example-quality checklist.
   - Document what makes a good Howl card: small, copyable, truthful,
     runnable-looking, and aligned with the Kujo ethos.
   - Keep this in README or a short `docs/example-authoring.md`.

## Items to avoid unless a real user need appears

- Network calls, AI generation, social posting, scheduling, telemetry, or
  registry dependencies.
- A full docs-site generator or web framework.
- Broad plugin architecture.
- Semantic Kujo checking inside Howl; use the Kujo interpreter or dedicated
  tooling for that.

## Suggested next starting point

Start with dark theme or nested `init`; both are user-visible, bounded, and good
demonstrations of Kujo's small-module style. Run the full verification checklist
after either change:

```bash
export KUJO=kujo
for f in src/*.kujo howl.kujo tests/howl_test.kujo; do
  "$KUJO" check "$f" || exit 1
done
./tests/run.sh
T=$(mktemp -d) && cd "$T" && \
  /Users/robertdevore/2026/Kujolang/kujo-repos/howl/bin/howl init && \
  /Users/robertdevore/2026/Kujolang/kujo-repos/howl/bin/howl validate && \
  /Users/robertdevore/2026/Kujolang/kujo-repos/howl/bin/howl render && \
  ls dist/howl/
```
