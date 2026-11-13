# Kujo showcase campaign

Twelve runnable examples: six **Built with Kujo**, six **Verified with Kujo**.

Open [the branded static gallery](gallery/index.html). Each entry links its source view, SVG, PNG, Markdown, execution receipt, and X draft. The [verification report](VERIFICATION.md) defines exactly what ran. [POSTS.md](POSTS.md) collects the twelve drafts; nothing has been posted.

## Reproduce

Requirements: Git, GitHub CLI (`gh`), Python 3, Bash, and a Node version supported by Lens's pinned `bridge/package.json`. The examples need no model credentials. Workcell only validates/inspects its definition, so this campaign does not require Docker. Bootstrap downloads released source, the platform runtime binary, Lens's locked dependencies, and Chromium.

From this directory:

```bash
python3 scripts/bootstrap.py --destination /tmp/kujo-showcase-releases
python3 scripts/verify.py --releases /tmp/kujo-showcase-releases --out /tmp/kujo-showcase-evidence
python3 scripts/verify-tool-commands.py --releases /tmp/kujo-showcase-releases --out /tmp/kujo-showcase-command-evidence
node scripts/render.mjs /tmp/kujo-showcase-releases
node scripts/audit.mjs /tmp/kujo-showcase-releases
```

Use a **new** destination/output directory. Verification refuses to overwrite earlier evidence. Add `--only lens` (or another card ID) to run one example. The render step deliberately uses the checked-in `evidence/verified/` and `evidence/tool-commands/` snapshots; it does not silently promote a rerun. Review a rerun's commands, assertions, and artifacts before deliberately replacing that snapshot and regenerating.

For a language example alone:

```bash
/tmp/kujo-showcase-releases/kujo run examples/bounded-map.kujo
```

For the original tool harness examples, `scripts/verify.py` sets `KUJO`, `KUJO_BIN`, `RELEASES`, `CAMPAIGN`, and `OUTPUT`, creates an isolated working directory, copies the declared inputs, and starts a loopback fixture server for Lens. The actual shell programs are `examples/*.sh`; expanded commands are captured in each `stderr.txt`. Source content, stdout, stderr, exit code, working directory, allowlisted environment values, and artifact hashes are retained. Temporary working directories are cleaned after execution. Absolute paths in receipts document the observed run; use the runner for portable replay.


## Short commands on the tool cards

The six tool cards and their HTML/Markdown source views use `commands/*.sh`, executed verbatim by `scripts/verify-tool-commands.py`. These are normal CLI/source-checkout invocations, not display-only replacements of executable names. The runner copies pinned release sources into temporary projects, places the actual launchers on PATH, prepares the existing fixtures, and captures expanded commands, stdout/stderr, exit codes, setup, and artifacts under `evidence/tool-commands/`. It requires local port 3000 to be free for the exact Lens URL shown on its card.

| Card | Required working context |
| --- | --- |
| Eval | Eval checkout with `eval.json` and `kennel.toml` present. |
| Workcell | `workcell` on PATH; current Git project contains `workcell.json`. |
| PackWrite | `packwrite` on PATH; current project contains `agent/` and `packwrite.toml`. |
| RunLedger | `runledger` on PATH; set `id` to the ID printed by `runledger start`; use the directory containing that ledger. |
| Lens | Lens checkout with `dashboard.json`; dashboard running at `http://127.0.0.1:3000/dashboard/`. |
| ShipCheck | ShipCheck checkout; `--dir .` checks that repository. |

The RunLedger verifier records its preparatory `start` command and actual `id`; the card shows finish/report/verify. The Workcell verifier initializes a disposable Git fixture before preflight. Existing tool limitations and original twelve-example evidence remain documented in the verification report.

## Howl workflow and presentation

Howl **1.2.0 is unchanged**. Its release was reviewed through README, AGENTS, CLI, manifest loading, SVG renderer, and tests. Howl validates paths and renders text; it does not execute examples. This campaign executes them separately before rendering.

- `catalog.json`: editorial intent, scope, pinned upstream links, and post copy.
- `howl.json`: all twelve cards; `built-with-kujo.json` and `verified-with-kujo.json`: six cards each.
- `generated/`: unmodified output from released Howl, including its static galleries.
- `gallery/`: publication copies. Markdown is byte-identical to Howl output. SVGs receive the explicit publication transform in `scripts/social-layout.mjs`; HTML receives a publication stylesheet and navigation/preview links.
- `assets/*-code.png`: deterministic, locally rendered source excerpts used through Howl's existing `background_image` field. They are code, not AI-generated art. Howl's existing `social` variant supplies the title, label, font, and border. The publication transform compacts the header above a full-width code panel, removes the wash/grain overlays, and removes the bottom-left accent line.
- `gallery/*.png`: Chromium rasterizations of the generated 1200×630 SVGs, after the embedded font loads.

The standard Howl SVG theme has a blue accent, rounded code panels, and system fonts. Rather than modify that renderer, every campaign card uses its supported `social` variant with Departure Mono, square framing, a white outer canvas with a dark code panel, and the official Kujo logomark. Published code uses 26–44 px Departure Mono with IDE-style syntax colors on #111, as requested in the latest visual revision. Keywords, strings, numbers, calls, JSON keys, and shell variables receive distinct colors; every palette color exceeds 7:1 contrast against the panel. Type size and leading fit each excerpt, preserving source line breaks where possible and centering the block vertically. The highlighting lexer preserves its input text exactly. Every card now shows exact text from its source or independently executed command snippet. Tool cards use short CLI commands from `commands/*.sh`; internal release paths remain in the execution harness only. No wash covers the code. The raw social outputs retain the upstream layout for auditing and are not the recommended review images. Original HTML output retains Howl's theme; publication-only CSS makes the gallery and source pages grayscale, square, and Departure Mono. Keep `generated/` as the auditable raw output.

Howl names its manifest field `expected_output`. Here that field contains **verbatim observed stdout**, never a prediction. Large JSON output is omitted from the card rather than rewritten; the complete output remains in the receipt directory. Howl's field label is unchanged, and each card's notes clarify the distinction. Social images use literal source excerpts; full runnable source is always available in HTML and Markdown.

## Source selection and boundaries

`catalog.json` records one problem and one scope explanation per card. Prefer canonical examples: the language examples reduce `test_parallel_simple`, HLP-013, HLP-015, and `secrets_redaction`; the two task examples extract released lifecycle contracts because no small task-control example exists under `examples/`. They are explicitly identified as contract extractions, not original upstream example files.

Eval uses its unchanged three-check release suite and copied manifest fixture. Workcell uses its unchanged hello definition. PackWrite uses the released `tests/fixtures/golden-agent` pack, since its canonical getting-started generation path needs a model call; only offline validation is demonstrated. RunLedger follows its README lifecycle using an explicitly scripted local run. Lens uses its canonical dashboard spec with the unsupported `selectors.not_exists` assertion removed, a small authored local page, and link checking enabled. ShipCheck gates its own pinned release checkout.

No speedup, token saving, cost, live provider, container enforcement, test-running capability of ShipCheck, or production readiness certification is implied. These are focused demonstrations, not exhaustive tool qualification.

## Asset provenance

Departure Mono and its license, and the official black Kujo logomark, were copied unchanged from `kujolang/docs.kujolang.ai` commit `12977e425e8be3923cc1882e6b51a0d71040c1f0`:

- `assets/sitekit/fonts/DepartureMono-Regular.woff2`
- `assets/sitekit/DepartureMono-LICENSE.txt`
- `assets/img/kujo-logomark-black.svg`

Upstream Kujo/tool files retain their original repository licenses. Pinned repositories and release commits are in `releases.json`; the PackWrite fixture's upstream location is `tests/fixtures/golden-agent/` at its pinned commit. Campaign artwork only combines these assets with the actual example source.
