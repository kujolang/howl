# Howl 1.2.0

Howl 1.2.0 strengthens the offline showcase workflow without changing the
Markdown, HTML, SVG or gallery formats. It requires Kujo 1.3.1 or newer.

## Safer input and output

- Contain example and asset paths, including symlink targets; require regular
  files and reject non-regular manifests before potentially blocking reads.
- Reserve `index` for the gallery and reject source/output collisions.
- Replace artifacts atomically, retain mtimes for identical output, and reject
  symlink destinations before writing. Forced init preflights both destinations.
- Isolate launcher imports from caller directories and support PATH symlinks.
- Escape Markdown prose and reject obfuscated active URL schemes.

## Less unnecessary work

Metadata commands avoid reading example or asset contents. Show loads the selected
example; rendering processes one card at a time. Standard SVG skips unused assets,
and transparent social SVG skips its background. Wrapping stops once overflow
is proven. Full public card models still retain all requested embedded assets.

The measured eight-card long-text SVG workload fell from a 6.172-second median
to 0.509 seconds with identical output. This is a stress-workload measurement,
not a general rendering speed claim; raw evidence is in the repository audit.

## CLI and installation

Select an ID beginning with `--` using `howl show -- --format`.
Place flags before the separator, for example `howl caption --platform x -- --format`.

With Kennel 1.1.0 or newer and its supported Kujo runtime:

```bash
kennel tool install howl@1.2.0
howl version
```

For project dependencies, use `kennel add howl@1.2.0`. The release now includes
its own `kennel.toml` and a native global command entry; old registry versions
remain unchanged. The repository launcher remains available with `KUJO` override.

## Compatibility and verification

The supported commands, manifest schema and artifact layouts remain stable.
Previously accepted unsafe paths and non-regular inputs now fail clearly.
Writes are atomic per file, not a multi-file transaction; input/output roots and
ancestors must be trusted. Howl never executes examples or posts content.

Run `./tests/verify.sh` for source checks, 106 unit assertions, CLI/filesystem
contracts, 48 wrapping cases, golden artifacts, 64 malformed-manifest cases,
deterministic rendering and no-op mtime checks.
