# Howl — session notes

## 2026-06-19 — production-readiness hardening review

- Reviewed the full repo shape after the move to `src/`. No obsolete root
  implementation files were found; the root keeps only the thin `howl.kujo`
  entrypoint, package/docs/examples/tests, and launcher.
- Hardened CLI option parsing: value flags now fail clearly when a value is
  missing, numeric limits must be positive integers, unknown options are
  rejected, and invalid `--format` / `--platform` values stop before work
  starts.
- Added render output path guardrails through `util.is_safe_output_dir`.
  Howl still supports normal relative paths and absolute custom directories,
  but refuses blank, root, current, parent, traversal, and ambiguous paths.
- Tightened manifest validation so bad top-level shapes, non-array `cards`,
  malformed `project` / `theme`, non-string required fields, non-string
  optional fields, and malformed `concepts` are reported as itemized manifest
  problems.
- Hardened Markdown output: manifest prose is escaped and fenced code blocks
  switch markers when the example text contains backticks.
- Removed stale `tests/howl_test.out`; it recorded an old failing result and
  was not referenced by the runner.
- Updated README with precise production-readiness language and refreshed
  security notes. Added `docs/next-session-review-2026-06-19.md` for the next
  improvement queue.
- Verification result: `kujo check` passed for all `src/*.kujo`, `howl.kujo`,
  and `tests/howl_test.kujo`; `./tests/run.sh` passed at **70 passed, 0
  failed**.

## 2026-06-12 — readability and search-hygiene cleanup

- Added canonical-example guidance to README and AGENTS: `examples/*.kujo` and
  `howl.json` are the copyable surfaces; `tests/` is a behavior-contract area.
- Documented search exclusions for future agent sweeps: `.git/`, `dist/`, and
  `tmp_test_*/`. `dist/howl/` is generated output and intentionally ignored.
- Added shell-level exact output contracts for `howl validate`, `howl list`,
  and `howl show clear-intent` before refactoring shared CLI print helpers.
- Refactored repeated CLI output shapes into tiny local helpers without
  changing user-visible text.

## 2026-05-29 — initial build (v1.0.0)

Built Howl from scratch: a standalone CLI in the Kujo language that turns
example files + a JSON manifest into SVG/Markdown/HTML showcase cards plus a
static gallery. Sibling of RunLedger and ChangeBudget; same project shape.

### Gotchas

- **Dialect mismatch on the first pass.** I initially wrote everything in a
  `fn`/`let`/`.get()`/`.set()` method style. The Kujo in this workspace uses
  `func`/`:=`/`null`/`d["k"]`/`has_key`/global `len split join push slice` —
  every file had to be rewritten. Lesson: read a sibling `src/*.kujo` *before*
  writing a line. `push` returns a new list; `replace` replaces all
  occurrences; null is `null` and is tested via `type(v) == "null"`.
- **One `for` loop per function scope** crashes `kujo check`
  (`Duplicate declaration __iter_2`). Used index-based `while` loops
  exclusively — every list walk is `mut i := 0; while i < n`.
- **`write_file` refuses to overwrite** on the VM. Centralized a `write_out`
  helper (delete-if-exists then write) in `cli.kujo`. Tests write each fixture
  to a fresh path under a unique temp dir, with a `put` helper that deletes
  first.
- **No `string + number`** — every numeric interpolation goes through
  `to_string(...)`.
- **SVG text does not reflow.** Had to write `wrap_words` (greedy word wrap
  with marked overflow), `emit_code` (clip columns, cap rows, append a "… N
  more lines" marker), and `rows_that_fit` (compute how many code rows fit the
  panel). The code panel height is derived from the remaining vertical space
  after the wrapped title + tagline, so variable-length titles don't collide
  with the code block.
- **VM "Index out of bounds: 1" from heavy list building.** The first cut of
  the HTML/SVG/gallery renderers built output by pushing dozens of fragments
  into a `mut arr := []` then `join`-ing. Past a certain number of `push`
  allocations in one call path the VM threw `KUJVM001 ... Index out of bounds:
  1` — and it reproduced calling `render_gallery` in complete isolation, so it
  was the renderer, not test-scope size. **Fix:** rewrote the three HTML/SVG
  renderers to single-string accumulation (`mut out := "..."; out = out + ...`)
  with the big CSS/`<style>` blocks as single string literals. That removed the
  per-fragment list churn and the crash went away; tests went green at **48
  passed / 0 failed**. Lesson: on this VM, prefer string concatenation over
  building-then-joining large lists in hot paths.
- **Harness output channel was unreliable this session.** The tool-output and
  even file-read channels intermittently injected fabricated/duplicated lines
  (e.g. a stack of identical `check`/`at put` frames, pages of `...`). I
  verified real results by writing a machine-readable `passed=N failed=N` line
  to a file and by trusting the process exit code from `tests/run.sh` rather
  than the streamed text. Ground truth: **48 passed, 0 failed**, runner exit 0,
  in under a second. Do not trust a noisy dump; pin down ground truth with a
  single deterministic artifact (a file or an exit code).

### Aha moments

- **Flatten everything into one card dict.** `manifest.build_card` reads the
  example file and applies truncation up front, so the three renderers are
  pure `(card, project) -> string` with zero I/O and trivial tests. Best
  structural decision — each renderer stayed ~100 lines.
- **Escaping has exactly one home.** `util.escape_html` (ampersand first!) is
  shared by the HTML and SVG renderers since XML entities are identical. One
  function, one stress test, no duplicated escaping logic. Verified against
  hostile input (`<script>`, `&`, quotes in title/concepts/project name):
  zero raw tags leak, entities present in both HTML and SVG.
- **String accumulation beats list+join on this VM.** Besides dodging the
  crash above, the single-string renderers are simpler to read and diff — a
  good fit for the Kujo low-noise ethos.
- **Determinism is a feature, not a limitation.** Captions are assembled from
  manifest fields only. The "don't invent claims" rule is enforced by
  construction: nothing in the code adds adjectives, benchmarks, or
  comparisons. That is what makes a Kujo example marketable without becoming
  hype — the code speaks, the metadata frames it, nothing is faked.
- **The Kujo ethos shaped the layout.** Small pure primitives, flat data, plain
  inspectable text artifacts, low-noise modules. The tool embodies what it
  showcases.

### Decisions made

- **JSON manifest** (`howl.json`) — matches the spec and the sibling tools'
  convention; serialized via `to_json_pretty` in `init` so generated manifests
  are always valid.
- **Validation collects all problems** before failing, so a user fixes a
  manifest in one pass rather than whack-a-mole.
- **`id` is validated, not rewritten.** Filesystem-safe ids keep output
  filenames stable and the manifest the source of truth (the shared gotcha
  notes `slugify` mangles ids anyway).
- **`--format` gates which files render**; `index.html` is written whenever
  HTML is in scope. Gallery links are relative so `dist/howl/` is portable.
- **One minimal light theme.** Resisted a theme/plugin architecture (explicit
  non-goal). `theme` and per-card `variant` are parsed but intentionally not
  yet wired to styling.

### Future improvements (intentionally skipped)

- Optional dark theme + wiring `variant` to per-card styling.
- PNG/raster export — would need an external rasterizer; only add if it can
  stay offline and optional.
- `--watch` / incremental render — wait for real usage before building.
- Per-format gallery columns or filtering — only if a real gallery gets big.

### Instructions for future agents

- Keep it small. Do not add a scheduler, poster, AI/network call, docs-site
  generator, or theme engine. Do not invent claims about Kujo.
- Read a sibling `src/*.kujo` for the dialect before editing.
- Run `./tests/run.sh` and check files one at a time after any change:
  `for f in src/*.kujo howl.kujo tests/howl_test.kujo; do "$KUJO" check "$f" || exit 1; done`.
- New card field → add it in `manifest.build_card`, then read it in renderers.
- Use `while`, not `for`. Use `to_string()` around numbers. Use `write_out`
  for any file you might re-render. `arr = push(arr, x)`. Prefer string
  concatenation over building-then-joining large lists in renderers. See
  `AGENTS.md` for the full gotcha list.
- Verify with the **exit code** of `./tests/run.sh` (0 = pass), not the
  streamed text — the harness display was unreliable during the build.
