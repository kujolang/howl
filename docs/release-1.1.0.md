# Howl 1.1.0 release notes

Howl 1.1.0 expands deterministic social-card production while preserving the
offline, inspectable renderer contract.

## Highlights

- Render branded 1200×630 social SVGs with embedded local image and font data.
- Hide frames and destination URLs independently, or emit a transparent
  overlay for an existing image pipeline.
- Add escaped SVG title/description metadata when a card supplies `alt`.
- Preserve file mtimes when a rebuild produces byte-identical output.
- Detect long-title overflow without the former array/string VM failure.
- Reject unknown variants and active-content URL schemes before rendering.
- Keep galleries, render counts, Markdown fences, truncation notices, font
  declarations, and social branding faithful to the requested output.

## Release qualification

Run the Kujo checks, unit contracts, and repository-local release regression:

```bash
for file in src/*.kujo howl.kujo tests/howl_test.kujo; do
  "$KUJO" check "$file" || exit 1
done
./tests/run.sh
python3 tests/release_regression.py
```

The release regression uses committed SHA-256 golden snapshots and a fixed seed
for manifest fuzzing. Intentional renderer changes require inspecting the
artifact diff before running `--update-golden`.

Downstream qualification must include `robertdevore.com`,
`python.robertdevore.com`, `kujolang.ai`, and `agents.kujolang.ai`. Publish the
tag only after their Howl artifacts reproduce byte-for-byte or every difference
has been explicitly reviewed, and after each site's own validator passes.
