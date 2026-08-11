# Howl — next-agent orientation guide

Read this before touching the code. It exists so you don't rediscover the repo
from scratch. The user-facing docs are in [README.md](README.md); this file is
the *builder's* map and does not duplicate it.

## Purpose

Howl is a small standalone CLI that turns Kujo example files + manifest
metadata into shareable showcase artifacts (SVG, Markdown, HTML, gallery). It
is offline, deterministic, and makes no claims of its own. See README for the
full product description and non-goals.

## Current status

v1.1.0, complete and working. All commands implemented (`init validate list
show caption render help version`). Tests pass (102 assertions). All `.kujo`
files pass `kujo check`. End-to-end render verified, including HTML/SVG
escaping of hostile input.

## This is built in the Kujo language

Howl is a sibling of [RunLedger](/path/to/runledger) and
[ChangeBudget](/path/to/changebucket) — same structure: a thin
`*.kujo` entrypoint, `src/*.kujo` modules, a `bin/` bash launcher, and a
`tests/run.sh` + `tests/*_test.kujo` harness. The **kujo repo at
`kujo` is reference-only** — do not modify Kujo core
to build Howl.

The Kujo interpreter is at `kujo`.
Set `KUJO` to it for every command below.

## Kujo dialect used here (important)

This codebase uses the same dialect as the sibling tools, which is **not** the
`fn` / `let` / `.get()` style:

- functions: `func name(...) { }`, exported with `export func`
- bindings: `x := ...` (declare), `x = ...` (reassign), `mut x := ...` for
  mutable locals
- null is `null` (check with `type(v) == "null"`); JSON parse error is
  `type(v) == "Error"`
- dicts: `d["k"]`, assign `d["k"] := v`, membership `has_key(d, k) == 1`
- lists: `len(arr)`, `arr[i]`, `push(arr, x)` **returns a new list** (use
  `arr = push(arr, x)`), `slice(arr, a, b)`
- strings are global builtins (no import): `len split join replace substring
  char_at index_of (-1 if absent) to_lower to_upper trim starts_with ends_with
  contains`. Note `replace` replaces **all** occurrences.
- JSON/FS: `parse_json to_json to_json_pretty read_file write_file delete_file
  file_exists create_dir list_dir`

## First files to read

1. `src/cli.kujo` — argv parsing, command dispatch, the only I/O module.
2. `src/manifest.kujo` — load/validate manifest, build the card data model.
3. `src/render_svg.kujo` — the trickiest renderer (fixed-layout text wrap).
4. `tests/howl_test.kujo` — shows the expected behavior of every module.

## Search hygiene and canonical examples

Prioritize copyable examples over tests: examples should model the most
token-efficient idioms we want agents to imitate.

Canonical example surfaces:

- `examples/*.kujo` — real examples rendered from `howl.json`.
- `howl.json` — manifest metadata and expected outputs for those examples.
- README snippets and `src/cli.kujo`'s `starter_example`/`starter_manifest` —
  onboarding copy users are likely to copy.
- For fixed starter text or help prose, prefer one literal string with `\n`
  escapes. Use push-built line arrays only when the content is genuinely
  assembled from data.

Tests and fixtures:

- `tests/howl_test.kujo` and `tests/run.sh` are behavior contracts. Keep exact
  output checks when refactoring CLI output, but do not shorten fixtures just
  for aesthetics when explicit output improves clarity.
- There are currently no stale, legacy, or expected-fail examples. If one is
  added later, label it in its file header and in the manifest or docs that
  reference it.

Generated/bulk paths:

- Exclude generated/bulk paths from the main sweep unless the task explicitly
  targets them; document the search exclusions you used.
- Current default exclusions: `.git/`, `dist/`, and `tmp_test_*/`.
- Useful pattern: `rg "term" --glob '!dist/**' --glob '!tmp_test_*/**'`.

## Commands

```bash
./bin/howl <command>        # run the CLI
./tests/run.sh              # run tests (writes/cleans tmp_test_* under root)
for f in src/*.kujo howl.kujo tests/howl_test.kujo; do
  kujo check "$f" || exit 1
done                        # lint
```

## Repo map

```
howl.kujo              entrypoint: main(args()) -> exit(code)
bin/howl               bash launcher (uses `kujo` by default, preserves cwd)
kujo.toml              package manifest (name/version)
src/
  util.kujo            escaping, ids, line-shaping, errors (pure, no I/O)
  manifest.kujo        load + validate + card data model (reads example files)
  caption.kujo         deterministic captions (+ X.com bounded variant)
  render_md.kujo       Markdown renderer
  render_html.kujo     standalone HTML renderer (embedded CSS)
  render_svg.kujo      1600x900 showcase + 1200x630 social SVG renderer
  gallery.kujo         static index.html
  cli.kujo             argv/opts parsing + command dispatch + file output
tests/
  howl_test.kujo       inline-harness unit + e2e tests
  run.sh               test runner
examples/              starter example(s)
docs/session-notes.md  build notes, gotchas, decisions
```

## Architecture

`cli.main(argv)` parses the command + options, then:

- **load_model**: `manifest.load_manifest` → `validate_manifest` (fail clearly
  on problems) → `build_cards`. A *card* is a flat dict with everything a
  renderer needs: metadata + the example file's (truncated) `code` +
  truncation flags. Renderers are pure functions `(card, project) -> string`
  and never touch the filesystem.
- **render** writes `<id>.{md,html,svg}` and `index.html` via `write_out`
  (delete-then-write, because the VM's `write_file` refuses to overwrite).

The card data model lives in `manifest.build_card`. If you add a field, add it
there and the renderers can read it via `card["..."]`.

## Ecosystem boundaries / non-goals

Do NOT turn Howl into a scheduler, poster, AI caller, docs site generator, web
framework, linter, or a reviewer. Do NOT make it depend on the network or
invent claims about Kujo. It does not replace Trail, Scout, PatchBrief,
RunLedger, ChangeBudget, SignalCheck, Eval, Spec, ShipCheck, or Concord. Keep
it small.

## Known gotchas (Kujo language)

These shaped the code — see `docs/session-notes.md` and the shared memory
`kujo-language-gotchas`:

- **One `for` loop per function scope** — `kujo check` errors otherwise. This
  code uses index-based `while` loops everywhere; keep doing that.
- **`write_file` refuses to overwrite** on the VM — use `write_out` (delete
  first). Tests use fresh paths under a unique temp dir.
- **No `string + number`** concat — wrap numbers in `to_string(...)`.
- **`push` returns a new list** — always `arr = push(arr, x)`.
- **`replace` replaces all occurrences** (no separate replace_all).
- **`test` is a reserved keyword** — don't name anything `test`.

## Verification checklist

```bash
for f in src/*.kujo howl.kujo tests/howl_test.kujo; do
  kujo check "$f" || exit 1
done                                                   # clean
./tests/run.sh                                          # passed=81 failed=0
T=$(mktemp -d) && cd "$T" && \
  "$OLDPWD/bin/howl" init && "$OLDPWD/bin/howl" validate && \
  "$OLDPWD/bin/howl" render && ls dist/howl/            # 4 artifact types
```

Confirm rendered HTML/SVG escape `<`, `>`, `&`, quotes (grep for `&lt;`,
`&amp;`; ensure no raw `<script>` from card content).

## Open questions / future improvements

See `docs/session-notes.md` → Future improvements. Headlines: optional dark
theme, per-card `variant` styling (field is parsed but currently unused),
PNG export (would need an external rasterizer — keep optional/offline).
