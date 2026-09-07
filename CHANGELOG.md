# Changelog

## Unreleased

- Contain symlinked inputs, require regular files, and reserve the gallery id.
- Write artifacts atomically and preserve existing output when a write fails.
- Isolate launcher imports and support the documented PATH symlink installation.
- Escape Markdown prose and reject control-prefixed active URL schemes.
- Defer content loading to commands and render one card at a time.
- Add filesystem/failure regression tests and a pinned-runtime CI gate.
- Require Kujo 1.3.1 filesystem primitives; valid artifact layouts stay unchanged.


All notable changes to Howl are documented here.

## Unreleased

## [1.1.0] - 2026-08-11

- Added launch-readiness Spec and Eval metadata for the Kujo prelaunch review.
- Added a 1200×630 `social` card variant with embedded local background images,
  embedded mono fonts, page labels, and destination URLs.
- Added frameless, URL-free, and fully transparent social-card modes plus
  optional accessible SVG title/description metadata.
- Preserved output mtimes on no-op rebuilds for cache-friendly downstream
  pipelines.
- Added deterministic golden snapshots, manifest-parser fuzzing, edge-case
  rendering checks, corpus benchmarking, peak-memory reporting, and JPEG pair
  verification for release qualification.
- Fixed long social titles that could trigger a Kujo VM array/string operation
  error while adding the overflow marker.
- Fixed nested custom-manifest initialization, strict variant and link-scheme
  validation, collision-proof Markdown fences, and visible truncation notices.
- Fixed format-aware galleries and render counts, WOFF declarations, unbroken
  social-title clipping, and project-derived social-card branding.
- Avoided repeating the same project brand and social label in card headers.

## [1.0.0] - 2026-06-27

- Prepared Howl for public release with deterministic showcase card generation, manifest validation, Markdown/HTML/SVG rendering, and offline test coverage.
