# Howl

[![Version](https://img.shields.io/badge/version-1.0.0-black)](https://github.com/kujolang/howl)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![built with Kujo](https://img.shields.io/badge/built%20with-Kujo-white.svg)](https://github.com/kujolang/kujo)

> Turn small Kujo examples into reviewable showcase artifacts.

Howl reads a manifest of *showcase cards* plus the real example files they
reference, and renders each card to **SVG**, **Markdown**, and **HTML**, along
with a static **gallery** (`index.html`). The output is usable in X.com drafts,
launch announcements, README sections, landing pages, blog posts, docs, GitHub
discussions, release notes, demo galleries, and agent-handoff examples.

Howl is **fully offline and deterministic** — the same inputs produce stable
outputs, so artifacts are safe to commit, diff, and review.

For contributor and agent sweeps, prioritize copyable examples over tests:
examples should model the most token-efficient idioms we want agents to
imitate.

| | |
| --- | --- |
| **Status** | v1.0.0 — stable |
| **Runtime** | The [Kujo](https://github.com/kujolang/kujo) interpreter (Howl is written in Kujo) |
| **Dependencies** | None. No network, no package registry, no external services |
| **Tests** | 70 assertions, filesystem-isolated, `./tests/run.sh` |
| **License** | MIT |

---

## Table of contents

- [Why Howl](#why-howl)
- [Production readiness](#production-readiness)
- [What Howl does not do](#what-howl-does-not-do)
- [Install](#install)
- [Quick start](#quick-start)
- [Command reference](#command-reference)
- [Manifest reference](#manifest-reference-howljson)
- [Example file handling](#example-file-handling)
- [Caption generation](#caption-generation)
- [Output artifacts](#output-artifacts)
- [Exit codes](#exit-codes)
- [Use in CI](#use-in-ci)
- [Security & privacy](#security--privacy)
- [Architecture](#architecture)
- [Kujo ethos](#kujo-ethos)
- [Limitations](#limitations)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Why Howl

Good examples sell a language. But turning a working snippet into something
shareable usually means hand-building cards in a design tool, copy-pasting code,
and re-doing it every time the example changes. That work is tedious, drifts out
of sync with the source, and quietly invites embellished claims.

Howl makes the example the source of truth. You keep real `.kujo` files in your
repo, describe them once in a manifest, and regenerate every artifact with one
command. Because rendering is deterministic and claim-free, what ships is
exactly what your code does — nothing invented, nothing stale.

## Production readiness

Howl is production-ready for its intended scope: an offline, deterministic CLI
that turns trusted project examples and manifest metadata into reviewable,
committable showcase artifacts. It is suitable for local workflows, CI gates,
release prep, documentation pipelines, and language-marketing repositories that
want stable output with no network or service dependency.

That does not make Howl an enterprise platform in the broad sense. It is not a
multi-tenant service, scheduler, CMS, poster, analytics product, package
manager, or semantic Kujo verifier. Its strength is narrower and sharper: small
inputs, clear validation, safe output escaping, portable static artifacts, and
behavior covered by tests.

## What Howl does **not** do

These are deliberate, permanent boundaries:

- It does **not** post to social media or schedule anything.
- It does **not** call AI/LLM or any network APIs — it never opens a socket.
- It does **not** invent claims: only fields present in your manifest are
  rendered. No benchmarks, adoption numbers, or comparisons are ever fabricated.
- It does **not** validate Kujo *semantics* — it renders your files as text.
- It does **not** replace Trail, Scout, PatchBrief, RunLedger, ChangeBudget,
  SignalCheck, Eval, Spec, ShipCheck, or Concord.

## Install

Howl runs on the Kujo interpreter, so you need a `kujo` binary.

```bash
git clone <this-repo> howl
cd howl

# Run via the bundled launcher. Point KUJO at your interpreter if `kujo`
# is not already on your PATH:
KUJO=/path/to/kujo/target/release/kujo ./bin/howl help

# …or invoke the entrypoint directly:
kujo run howl.kujo -- help
```

To use `howl` from anywhere, symlink the launcher onto your `PATH` and export
`KUJO` in your shell profile:

```bash
ln -s "$PWD/bin/howl" /usr/local/bin/howl
echo 'export KUJO=/path/to/kujo/target/release/kujo' >> ~/.zshrc
```

> The launcher preserves your working directory, so `howl` always resolves
> `howl.json` and output paths relative to where you invoke it.

## Quick start

```bash
howl init        # scaffold howl.json + examples/ (never overwrites)
howl validate    # check the manifest and that referenced files exist
howl list        # list the cards
howl render      # write dist/howl/*.{svg,md,html} + index.html
```

Open `dist/howl/index.html` in any browser — no server, no network, no build
step.

### Canonical examples

The root `examples/*.kujo` files are the canonical, copyable examples rendered
by `howl.json`. Their expected outputs are:

| Example | Expected output |
| --- | --- |
| `examples/clear-intent.kujo` | `Ready, agent` |
| `examples/safe-refactor.kujo` | `10` |
| `examples/agent-handoff.kujo` | `review` |

`tests/` contains fixtures and output contracts, not style examples to copy.
`dist/howl/` is generated render output and is ignored; regenerate it with
`howl render` instead of editing it by hand.

## Command reference

| Command | Description |
| --- | --- |
| `howl init` | Scaffold `howl.json` and `examples/` with one starter card. Skips existing files unless `--force`. |
| `howl validate` | Validate the manifest and that every referenced file exists. |
| `howl list` | List cards: id, title, file, concepts. |
| `howl show <id>` | Print one card's metadata and a code preview. |
| `howl caption <id>` | Print a deterministic share caption (`--platform x` for an X.com-bounded variant). |
| `howl render` | Render all cards to the output directory. |
| `howl help` | Show usage. |
| `howl version` | Show the version. |

### Options

| Option | Applies to | Default | Meaning |
| --- | --- | --- | --- |
| `--manifest PATH` | all | `howl.json` | Manifest file to read. |
| `--out DIR` | `render` | `dist/howl` | Output directory. |
| `--format FMT` | `render` | `all` | One of `all`, `svg`, `html`, `markdown`. |
| `--platform x` | `caption` | – | X.com-friendly caption, trimmed to 280 chars on a word boundary. |
| `--max-code-lines N` | `render`, `show` | `40` | Code lines per card before truncation. |
| `--max-output-lines N` | `render`, `show` | `20` | Expected-output lines per card before truncation. |
| `--force` | `init` | off | Allow `init` to overwrite existing files. |

```bash
# Render only SVGs for a specific manifest into a custom directory:
howl render --manifest ./showcase/howl.json --out ./public/cards --format svg
```

## Manifest reference (`howl.json`)

```json
{
  "project": {
    "name": "Kujo",
    "tagline": "Programming language for AI-native software",
    "url": ""
  },
  "theme": { "name": "minimal", "mode": "light" },
  "cards": [
    {
      "id": "clear-intent",
      "title": "Clear intent over boilerplate",
      "tagline": "Kujo favors code that humans and agents can continue safely.",
      "file": "examples/clear-intent.kujo",
      "language": "kujo",
      "concepts": ["clear intent", "agent-readable code", "low-noise syntax"],
      "expected_output": "Ready, agent",
      "caption": "AI-native software needs code that explains intent without burying it in ceremony.",
      "cta": "Kujo: programming language for AI-native software."
    }
  ]
}
```

**Required card fields:** `id`, `title`, `file`.

**Optional card fields:** `tagline`, `language`, `concepts`, `expected_output`,
`caption`, `cta`, `notes`, `url`, `variant`.

**Validation rules:**

- The manifest must be a JSON object and `cards` must be an array.
- `id` must be filesystem-safe (`a-z`, `0-9`, `-`, `_`) and unique across cards.
- Required fields must be strings; `title` must not be empty.
- Optional string fields must be strings when present; `concepts` must be an
  array of strings when present.
- The referenced `file` must exist and stay within the manifest directory tree.
- Missing optional fields never fail rendering.
- Invalid manifests produce a clear, itemized list of every problem at once.

Manifest `file` paths are resolved relative to the manifest's own directory and
cannot escape that directory tree, so a manifest is portable as long as its
examples travel with it.

## Example file handling

Howl reads `.kujo`, `.md`, `.txt`, and any other text file a card references. It
preserves indentation, escapes content safely for rendered markup, adapts
Markdown code fences when examples contain backticks, and truncates oversized
examples with an honest on-card notice rather than silently dumping them:

| Limit | Default | Override |
| --- | --- | --- |
| Code lines per card | 40 | `--max-code-lines N` |
| Code characters per card | 4000 | — |
| Expected-output lines | 20 | `--max-output-lines N` |

## Caption generation

Captions are deterministic — the same card always produces the same text. No AI,
no randomness, no invented claims.

1. If a card has an explicit `caption`, Howl uses it verbatim.
2. Otherwise it builds one from `title` + `tagline`.
3. A call-to-action is appended from the card's `cta`, falling back to the
   project name + tagline.

`--platform x` collapses the caption into a single block trimmed to 280
characters on a word boundary. **Howl only formats text; it never posts.**

```text
Clear intent over boilerplate.

Kujo favors code that humans and agents can continue safely.

Kujo: programming language for AI-native software.
```

## Output artifacts

`howl render` writes to `dist/howl/` (or `--out`):

| File | Purpose |
| --- | --- |
| `<id>.md` | Portable Markdown for READMEs, blogs, and discussions. |
| `<id>.html` | Standalone page with embedded CSS and no remote assets. |
| `<id>.svg` | 1600×900 social card, system fonts only, no external assets. |
| `index.html` | Static gallery linking every card's three artifacts. |

Every artifact is self-contained, works with no network access, and has all
card-derived text escaped before output.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success. |
| `1` | A usage error, an invalid manifest, or an unknown command. |

This makes `howl validate` and `howl render` safe to gate a build on.

## Use in CI

Because Howl is offline and deterministic, it drops cleanly into a pipeline —
validate on every change, and optionally fail if regenerated artifacts drift
from what's committed:

```bash
#!/usr/bin/env bash
set -euo pipefail
export KUJO=/path/to/kujo

howl validate                       # fail the build on a broken manifest
howl render --out dist/howl         # regenerate artifacts

# Optional: ensure committed artifacts are up to date.
git diff --exit-code dist/howl
```

## Security & privacy

- **No network.** Howl never opens a connection; artifacts reference no remote
  fonts, scripts, or stylesheets.
- **Output is escaped.** All untrusted card content (titles, code, concepts,
  project name) is escaped before it reaches HTML/SVG, and manifest prose is
  escaped in Markdown. Example text containing `<script>`, `&`, quotes, or code
  fences cannot break out of the intended artifact structure.
- **Manifest paths are contained.** Example files stay within the manifest
  directory tree; `../` traversal is rejected before Howl reads the file.
- **Output paths are guarded.** Render output rejects blank, root, current
  directory, traversal, and ambiguous paths before writing.
- **Options fail clearly.** Missing option values, invalid formats, invalid
  caption platforms, unknown flags, and non-positive line limits stop with
  friendly `howl:` errors.
- **No telemetry.** Howl collects nothing and phones home to no one.

## Architecture

```
howl.kujo              entrypoint: main(args()) -> exit(code)
bin/howl               bash launcher (respects $KUJO, preserves cwd)
src/
  util.kujo            escaping, ids, line-shaping, errors (pure, no I/O)
  manifest.kujo        load + validate + build the card data model
  caption.kujo         deterministic captions (+ X.com bounded variant)
  render_md.kujo       Markdown renderer
  render_html.kujo     standalone HTML renderer (embedded CSS)
  render_svg.kujo      1600x900 SVG renderer (manual text wrap/clip)
  gallery.kujo         static index.html
  cli.kujo             argv parsing, command dispatch, file output
tests/                 filesystem-isolated test harness + runner
examples/              example .kujo files for the starter manifest
```

The manifest is parsed and validated into one flat dict per card — metadata plus
the example's (already-truncated) code. The three renderers are pure functions
`(card, project) -> string` with no I/O, which keeps them small and trivially
testable. Only `cli.kujo` touches argv, stdout, and the filesystem.

## Kujo ethos

Howl is built to showcase — and to embody — the Kujo ethos:

> Kujo is an AI-native programming language focused on clear intent, low-noise
> code, and safe agent collaboration. Prefer semantic clarity over mechanical
> repetition. Keep code explicit, testable, and easy to diff. Favor small,
> obvious primitives over clever abstractions. The best Kujo code should be
> durable, inspectable, token-efficient, and easy for the next developer or
> agent to continue.

The renderers are small and pure, the data model is one flat dict per card, and
every artifact is plain text you can read and diff.

## Limitations

- The SVG layout is fixed-size; text is wrapped and clipped to fit (it is not a
  full text-layout engine).
- Theming is intentionally minimal — one light theme. The `theme` and per-card
  `variant` fields are parsed but not yet wired to styling.
- Howl renders `.kujo` files as text; it does not run or type-check them.

## Development

```bash
# Run the test suite (filesystem-isolated, no network):
KUJO=/path/to/kujo/target/release/kujo ./tests/run.sh      # 70 assertions

# Lint every module:
for f in src/*.kujo howl.kujo tests/howl_test.kujo; do
  /path/to/kujo/target/release/kujo check "$f" || exit 1
done
```

See [AGENTS.md](AGENTS.md) for a contributor/agent orientation guide and
[docs/session-notes.md](docs/session-notes.md) for build notes and decisions.

## Contributing

Howl is intentionally small. Before adding a feature, check it against
[What Howl does not do](#what-howl-does-not-do) — scope creep toward a poster,
a docs-site generator, or a network client will be declined. Bug fixes,
escaping hardening, renderer polish, and documentation are all welcome.

All changes must keep `kujo check` clean and `./tests/run.sh` green.

## License

MIT — see [LICENSE](LICENSE).
