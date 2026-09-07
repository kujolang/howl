# Howl repository hardening — 2026-09-07

## Repository and scope

- Repository: `kujolang/howl`, branch `main`.
- Starting SHA: `5470f928c5b563599778bbdf8ea0671211d3a265`, clean working tree.
- Ending implementation/verification SHA: `468799ef417826c8b2935c129fd81fab038296c8`
  (implementation `5879b9c66d05a8dabd36724ffd430f8936391d75`). This report is
  committed separately; its enclosing commit is discoverable with
  `git log -1 --format=%H -- docs/audits/repository-hardening.md` rather than
  attempting to embed a commit's own hash in its contents.
- Purpose: offline CLI converting manifest metadata and example text into
  deterministic Markdown, HTML, SVG, and a gallery for humans and publishing agents.
- Runtime: Kujo 1.3.1; inspected runtime SHA
  `9cedbf2f5ae5a0a9b126b055f4c9a6a58a2c23eb`. No registry/package dependencies
  in `kujo.toml`; Bash launcher, Python standard-library verification tooling.
- Integrations: Kujo module/filesystem contracts; four downstream site corpora;
  Eval command definitions and the release Spec; external rasterization remains
  outside Howl. No runtime network, model providers, MCP service, database,
  scheduler, worker pool, credentials, or telemetry.
- Write scope stayed within Howl, apart from explicitly requested Strata and
  SignalBox records. Downstream outputs were generated in disposable directories.
- Searches excluded `.git/`, `dist/`, `tmp_test_*/`, and audit scratch. All source
  modules, launcher, unit/CLI/release tests, fixtures, manifests, examples,
  agent instructions, release docs, and CI/ignore policy were inspected.

## Baseline

Before source changes, all ten source/test `kujo check` invocations passed;
`./tests/run.sh` passed 102 unit assertions and the existing CLI contracts.
`tests/release_regression.py` passed 13 golden artifacts, deterministic rebuilds,
mtime preservation, escaping, layout, contrast checks, and 64 seeded malformed
manifests. Root corpus: three cards, cold render 0.400s, no-op 0.566s,
peak RSS 15,605,760 bytes. These are single observations, not performance budgets.

The eight-card workload in `tests/benchmark.py` was run before changes, with
five samples per command and a shared 65,536-byte asset. See
[evidence/baseline-benchmark.json](evidence/baseline-benchmark.json).

The first new boundary test failed against the original implementation:
`validate` accepted a symlink to an outside file with exit 0. Separately, the
original launcher printed `SHADOWED` from a caller-provided `src/cli.kujo`;
the fixed launcher validates the intended manifest instead. The harmless
before/after receipt is [recorded here](evidence/runtime-import-shadow.json).

No existing repository test failure was found. During later verification,
macOS process-slot exhaustion intermittently prevented process creation or
returned exit 128. `ps` observed over 1,100 Git children of the Codex process.
Those host failures were retained separately and never accepted as passing
checks. No tests were weakened and no retry/sleep workaround was introduced.

## Findings

| ID | Priority | Area | Finding | Evidence | Action | Status |
|---|---|---|---|---|---|---|
| H01 | P0 | Input containment | Lexical paths allowed symlinks outside the manifest tree | Baseline boundary test; `resolve_contained_path` never inspected the filesystem | Canonical containment and descriptor-relative no-follow reads; allow in-tree links | Fixed |
| H02 | P0 | Module loading | Caller cwd could replace `src.cli` before Howl started | `SHADOWED` reproduction; Kujo module search roots | Import from launcher repository, then restore caller cwd | Fixed in launcher; runtime follow-up below |
| H03 | P1 | Data integrity | Changed artifacts were deleted before replacement was written | Original `write_out`; concurrent-reader and failed-write tests | Atomic replacement, checked failures, unchanged-content fast path, atomic no-overwrite init | Fixed |
| H04 | P1 | Output collisions | Card `index` overwrote its HTML with the gallery; output could overwrite a referenced input | Output filenames in `cmd_render`; source-preservation regression | Reserve `index`; preflight canonical input/output collisions and invalid targets | Fixed |
| H05 | P1 | Markup safety | HTML escaping did not stop Markdown links/fence header CR; URL filtering missed leading C0 controls | Original `render_md`, URL predicate probe; new hostile inputs | Escape Markdown punctuation, reject CR fence language, normalize leading URL controls | Fixed |
| H06 | P1 | I/O and memory | List/caption/show loaded all examples and encoded all assets; render retained all full cards | Original `load_model` → `build_cards`; oversized unused-asset regression | Metadata projection, selected preview, format-aware asset loading, one full card at a time | Fixed |
| H07 | P1 | Failure semantics | Filesystem failures could escape as VM errors; absent assets could silently become empty data | Original input/output helpers | CLI exception boundary; explicit read/write failures; regular-file validation | Fixed |
| H08 | P1 | Test isolation | Runner swept every `tmp_test_*` tree, including another invocation's fixtures | Original `find … rm -rf`; timestamp-derived unit directory | Pass an owned `mktemp` root; trap removes only that root | Fixed |
| H09 | P2 | Installation | Documented PATH symlink resolved the wrong project root | Original `BASH_SOURCE` parent calculation | Resolve relative/absolute launcher links before dispatch | Fixed |
| H10 | P1 | Regression gates | CI only checked artifact ignore rules | Original workflow inventory | Pinned-runtime source, shell, CLI, filesystem, golden and fuzz gate | Implemented |
| H11 | P2 | Docs/agent context | Stale 81-assertion instruction, unused-variant claim, and delete-first guidance | AGENTS versus implementation | Correct focused guidance; one complete verification entrypoint | Fixed |

## Changes and compatibility

### Filesystem and launcher boundaries

`src/manifest.kujo` keeps lexical validation, canonicalizes actual targets,
requires regular files, and resolves in-tree symlinks before calling Kujo's
`read_file_beneath` / `read_binary_file_beneath`. These primitives walk relative
components without following replacement symlinks and bound each read to the
qualified runtime's existing 8 MiB limit. They reject growth beyond the limit
instead of silently truncating input. Direct `resolve_file` keeps its lexical
return-path convention. Existing direct-model tests still prove rejected
traversal never becomes rendered example text.

`src/cli.kujo` preflights artifact targets against the manifest and all input
references, uses `write_file_atomic`, preserves identical mtimes, and converts
runtime exceptions into a nonzero `howl:` diagnostic. The no-force init path
uses atomic no-overwrite creation. Tests prove a read-only output directory
preserves old bytes, a concurrent reader sees complete old/new content, and
no atomic temporary files remain. Permission tests execute for non-root users;
they are inapplicable under root. The actual audit ran as a non-root user.

`bin/howl` resolves symlinks and relative `KUJO` executables before changing cwd.
Modules load from Howl's repository; a private `--howl-caller-dir` launcher
preamble restores the original cwd inside the CLI before user arguments are
parsed. User commands, normal output text, and relative manifest/output paths
keep their established behavior. Direct `kujo run howl.kujo` still follows
Kujo's module-search policy; prefer the launcher outside this repository.

### Command-specific content loading

`card_metadata` centralizes normalization. `build_card_preview` reads and
truncates one example without assets. Existing exported `build_card` and
`build_cards` still provide complete renderer models. CLI list/caption validate
all references but do not read their contents; show loads only the selected
example. HTML/Markdown-only render skips binary assets. Render retains one
full card and metadata for the gallery, with no persistent cache/invalidation
scheme. An unused 9 MiB asset succeeds for metadata/HTML and fails when SVG
actually needs it; an unrelated invalid UTF-8 example no longer breaks show.

### Markup, tests, and documentation

`src/render_md.kujo` escapes backslashes, brackets, backticks, asterisks and
underscores in manifest prose; source text remains in adaptive fences. CR and
LF are disallowed in the fence language. `src/util.kujo` removes leading C0
controls before checking active URL schemes, matching the
[URL parser's input normalization](https://url.spec.whatwg.org/#concept-basic-url-parser).

`tests/hardening_regression.py` exercises the real launcher and temporary
filesystem. The existing unit suite remains intact. Fuzz checks now demand
exit 1 and a `howl:` diagnostic instead of accepting any nonzero exit.
`tests/run.sh` also executes all three canonical examples and compares exact
outputs. `tests/verify.sh` combines source, shell, unit, CLI, filesystem, and
release checks. CI pins both checkout and Kujo source, builds with locked
Cargo inputs and no unused optional runtime features, then runs the same gate.
No benchmark threshold was added to CI.

README, AGENTS and CHANGELOG now explain the qualified runtime, command loading,
atomicity scope, launcher behavior, and authoritative verification command.
Historical session notes remain historical; unused exported helpers and release
fixtures were preserved because external consumers cannot be ruled out.

| Contract | Result |
|---|---|
| Public APIs | Existing exported signatures and valid complete-card fields preserved; metadata/preview helpers added |
| CLI | Same public commands/options, receipts and 0/1 status convention; filesystem failures consistently fail; private launcher cwd preamble added |
| Invalid inputs | Escaping symlinks, non-files, `index`, active/control-prefixed URLs, and input/output collisions now rejected |
| Formats/schemas | No manifest schema or artifact layout redesign; hostile/formatting Markdown prose is emitted literally |
| Config/environment | No public config key or environment variable added; `KUJO` retained; qualified filesystem primitives required |
| Consumers | Existing HTML/SVG/galleries and golden fixtures preserved; Markdown punctuation changes are intentional and reviewed below |
| Migration | Rename a card named `index`; keep assets/examples within the manifest tree; use real artifact files and a separate output directory |

## Performance and efficiency

The table reports all three observed runs of the same eight-card workload,
including the initial baseline rather than hiding host variation. Each median
uses five samples. The frozen baseline rerun uses an archive of the starting
SHA and a neutral caller cwd; it precedes the final run. Raw samples are in
[evidence/paired-before-benchmark.json](evidence/paired-before-benchmark.json)
and [evidence/after-benchmark.json](evidence/after-benchmark.json).

| Command | Initial baseline median | Frozen-baseline rerun median | Final median |
|---|---:|---:|---:|
| `list` | 0.337813s | 0.471421s | 0.403604s |
| `caption card-0` | 0.305636s | 0.497262s | 0.345015s |
| `show card-0` | 0.267627s | 0.473554s | 0.378089s |
| `render --format html` | 0.409762s | 0.822903s | 0.735521s |

Single root-corpus observations: baseline cold/no-op 0.400s/0.566s; final
complete gate 0.999s/0.897s. Peak RSS: baseline 15,605,760 bytes; final separate
`/usr/bin/time -l` observation 15,941,632 bytes. Root output remains 10 files,
17,360 bytes. The root fixture and release goldens preserve byte identity.
These runs include substantial host scheduling noise; filesystem probes and
atomic sync are real added work. No uniform latency/RSS improvement or stable
percentage claim follows from these observations.

### Downstream qualification

Compared archived starting implementation against the hardened implementation
using disposable output directories and current manifests:

| Corpus | Cards | Artifacts | Byte-identical | Changed Markdown |
|---|---:|---:|---:|---:|
| robertdevore.com | 169 | 508 | 502 | 6 |
| python.robertdevore.com | 27 | 82 | 82 | 0 |
| kujolang.ai (`kujolang.ai-work/howl-social.json`) | 194 | 583 | 544 | 39 |
| agents.kujolang.ai | 94 | 283 | 283 | 0 |
| Total | 484 | 1,456 | 1,411 | 45 |

Every HTML, SVG and gallery file is byte-identical. The 45 Markdown files have
86 changed lines, all solely punctuation encoded as literal numeric entities;
source fences and contents are preserved. Full diffs and the compact receipt
are in [evidence/downstream-diffs.txt](evidence/downstream-diffs.txt) and
[evidence/downstream-review.txt](evidence/downstream-review.txt). The subsequent
redundant-resolution cleanup was qualified by the complete local gate; it does
not alter rendering strings. No downstream publishing or regeneration in place
was performed, and site-specific validators/rasterizers were not run because
no site code or rendered files were changed.

The eight-card benchmark's list/caption/show/HTML stdout remains exactly
360 / 11 / 712 / 43 bytes respectively. Source-level I/O accounting changes
asset reads/base64 encodings from eight to zero for these four commands;
list/caption example reads go from eight to zero, show from eight to one.
These counts are code-supported, not syscall-trace measurements. The oversized
unused-asset regression locks in the loading boundary behaviorally.

Runtime dependencies remain zero Kujo packages. No Howl native binary is
built, and no dependency was replaced with custom cryptography/parsing. The
repository has no model prompts or MCP schemas, so token savings are not
claimed. Agent efficiency comes from one gate, concise receipts, exact errors,
and on-demand content. Large manifests remain buffered and gallery metadata
grows with card count; no speculative hard card cap or persistent cache was added.

## Coverage and remaining scope

| Review dimension | Result |
|---|---|
| Complexity/dead weight | Inspected every module and wrapper; shared metadata normalization removes eager construction; no unproven removals |
| Runtime/resources | Removed unused content loads and full-card retention; file reads bounded; per-file writes atomic; no leaks/caches/background workers added |
| Token/output | No model paths; normal CLI text preserved, verbose evidence stored here; docs point to one gate |
| Failures | Missing/non-file/outside inputs, malformed JSON/types, unsafe outputs, permission failure, invalid UTF-8, unknown formats/options checked |
| Security | Paths, symlinks, module shadowing, output collision, HTML/SVG/Markdown escaping, URL schemes, subprocess quoting and temp ownership reviewed |
| Concurrency/state | Concurrent artifact reader and isolated test roots; per-file atomicity, not multi-file transactions |
| APIs/dependencies | Valid public model contracts retained; zero registry dependencies; qualified Kujo filesystem APIs and pinned CI inputs |
| Documentation/examples | Three canonical examples execute with exact documented results; stale operational instructions corrected |
| Determinism | Existing SHA-256 goldens, clean rerender equality and no-op mtimes retained |

## Cross-repository follow-up

**Kujo runtime — P1, module-resolution policy.** At inspected runtime SHA
`9cedbf2f5ae5a0a9b126b055f4c9a6a58a2c23eb`, `src/module.rs` starts search paths
with cwd, while `src/main.rs::entry_script_search_paths` appends the entry
script's root. A caller-controlled `src/cli.kujo` can replace an installed
program's import. The local harmless reproduction is in
[evidence/runtime-import-shadow.json](evidence/runtime-import-shadow.json).
Impact: sibling launchers/direct absolute entrypoint execution may execute
caller code. Recommend an explicit entry-root-first/isolated module mode with
regression coverage. Review compatibility with intentional cwd overrides before
changing the default. Howl's fixed launcher does not require that runtime
change; direct invocations and sibling launchers still require review. No
sibling source was modified.

## Remaining work

- P0: none identified within Howl's supported local-project boundary.
- P1: runtime module-resolution follow-up above; Howl launcher is mitigated.
  SignalBox capture `cap_e3875c52-9264-4348-9f3b-6c91311784cb`, signal
  `sig_7180f1cf-ff35-402d-980b-0ec9d5e29697`; both verified by exact ID and
  concept search. No duplicates found; resolved work was rejected for capture.
- P2: no additional high-confidence local defect left open by this audit.
- Needs more evidence: stable-host latency/RSS profiling before claiming speed
  improvements or adding budgets. Shared-asset caching and early word-wrap
  termination need representative profiles and compatibility evidence.
- Not worth changing: arbitrary cosmetic refactors, removing possibly public
  helpers, adding a cache/server/watch process, or introducing token tooling
  where no model calls exist.
- Scope limits: input/output roots and their ancestors are trusted local
  directories; this is not a multi-tenant sandbox. Per-file atomic replacement
  does not guarantee an all-or-nothing gallery after disk failure or simultaneous
  publishers. Asset contents are embedded without semantic decoding. Site
  deployment, rasterizer changes, publication and tagging are outside this pass.

## Verification receipt

Commands ran from the Howl repository with
`KUJO="$PWD/../kujo/target/release/kujo"` (absolute when used by subprocesses).

| Command | Result |
|---|---|
| `for f in src/*.kujo howl.kujo tests/howl_test.kujo; do "$KUJO" check "$f" || exit 1; done` | Baseline PASS; final gate also checks examples |
| `./tests/run.sh` | Baseline and final PASS; original 102 unit assertions retained |
| `python3 tests/release_regression.py --site howl=howl.json --benchmark howl=howl.json` | Baseline PASS; qualified later through complete gate |
| `python3 tests/hardening_regression.py` | Baseline failed on outside symlink; final PASS via runner |
| `./tests/verify.sh` | PASS; source, examples, shell syntax, all tests, 13 goldens, 64 strict fuzz cases, root deterministic/no-op corpus |
| `python3 tests/benchmark.py` | Five samples per command before and after; informational timing only |
| `bash -n bin/howl tests/run.sh tests/verify.sh` | PASS |
| `python3 -m py_compile tests/hardening_regression.py tests/benchmark.py tests/release_regression.py` | PASS |
| `git diff --check` | PASS |
| `bash .github/scripts/check-kujo-tool-artifacts.sh 5470f928c5b563599778bbdf8ea0671211d3a265 HEAD` | PASS |
| `python3 tests/benchmark.py --howl .audit-local/before/bin/howl` | Frozen starting-SHA comparison PASS |
| `python3 docs/audits/evidence/compare-downstream.py` | 484 cards compared; review receipt above |
| `/usr/bin/time -l ./bin/howl render --out .audit-local/rss-final` | PASS; RSS recorded above |

Detailed low-volume receipts are under `evidence/`. Failed intermediate edits
were corrected before the passing complete gate; unchanged golden hashes were
not regenerated to mask drift. Host process-exhaustion interruptions do not
count as repository test passes.

For the archived comparison, the exact setup was
`mkdir -p .audit-local/before` followed by
`git archive 5470f928c5b563599778bbdf8ea0671211d3a265 | tar -x -C .audit-local/before`.
The corpus comparison script is preserved in `evidence/compare-downstream.py`
(the initial execution used the identical audit scratch driver). It expects
the four documented local downstream checkouts and writes only scratch output.

GitHub Actions qualified the introduced gate at
`1c321622cb38a20ecaaac87dcca83134d354d9f3`:
[Howl verification run 34083627277](https://github.com/kujolang/howl/actions/runs/34083627277)
and the artifact guard both passed. Final local gate receipt corresponds to
`468799ef417826c8b2935c129fd81fab038296c8`.
