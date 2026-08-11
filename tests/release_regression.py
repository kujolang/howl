#!/usr/bin/env python3
"""Deterministic release gate for Howl renderers and downstream corpora."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "release" / "howl.json"
GOLDEN = ROOT / "tests" / "golden" / "release-fixture.sha256.json"


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"{result.stdout}{result.stderr}"
        )
    return result


def hashes(directory: Path, suffixes: tuple[str, ...] = (".svg", ".md", ".html")) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.suffix in suffixes
    }


def contrast(a: str, b: str) -> float:
    def luminance(value: str) -> float:
        channels = [int(value[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def verify_fixture(binary: str, update_golden: bool) -> None:
    with tempfile.TemporaryDirectory(prefix="howl-release-fixture-") as raw:
        base = Path(raw)
        first = base / "first"
        second = base / "second"
        run([binary, "validate", "--manifest", str(FIXTURE)])
        run([binary, "render", "--manifest", str(FIXTURE), "--out", str(first), "--format", "all"])
        first_hashes = hashes(first)
        first_mtimes = {path: path.stat().st_mtime_ns for path in first.rglob("*") if path.is_file()}
        time.sleep(0.02)
        run([binary, "render", "--manifest", str(FIXTURE), "--out", str(first), "--format", "all"])
        assert first_mtimes == {path: path.stat().st_mtime_ns for path in first.rglob("*") if path.is_file()}, "no-op rebuild rewrote outputs"
        run([binary, "render", "--manifest", str(FIXTURE), "--out", str(second), "--format", "all"])
        assert first_hashes == hashes(second), "fixture rendering is not deterministic"

        if update_golden:
            GOLDEN.parent.mkdir(parents=True, exist_ok=True)
            GOLDEN.write_text(json.dumps(first_hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        assert GOLDEN.exists(), "golden snapshot is missing; run with --update-golden after review"
        expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
        assert expected == first_hashes, "rendering drifted; inspect output and use --update-golden only for an intentional change"

        hostile_html = (first / "escaping-unicode.html").read_text(encoding="utf-8")
        hostile_md = (first / "escaping-unicode.md").read_text(encoding="utf-8")
        hostile_svg = (first / "escaping-unicode.svg").read_text(encoding="utf-8")
        for body in (hostile_html, hostile_md, hostile_svg):
            assert "Zażółć" in body and "日本語" in body
        assert "<script>alert" not in hostile_html and "<script>alert" not in hostile_svg
        assert '<script>alert("howl")</script>' in hostile_md
        assert "&lt;script&gt;" in hostile_html and "&lt;script&gt;" in hostile_svg
        assert "````text" in hostile_md

        long_svg = (first / "long-social.svg").read_text(encoding="utf-8")
        assert 'width="1200" height="630" viewBox="0 0 1200 630"' in long_svg
        assert "…" in long_svg and "data:image/svg+xml;base64," in long_svg and "data:font/woff2;base64," in long_svg
        assert "role=\"img\"" in long_svg and "<title " in long_svg and "<desc " in long_svg
        ET.fromstring(long_svg)

        transparent = (first / "transparent-frameless.svg").read_text(encoding="utf-8")
        assert 'x="42" y="42" width="1116" height="546"' not in transparent
        assert "https://example.test/hidden/" not in transparent
        assert 'fill="url(#wash)"' not in transparent and 'fill="#f4f4f1"' not in transparent and "<image href=" not in transparent

        fallback = (first / "fallback-social.svg").read_text(encoding="utf-8")
        assert 'fill="#f4f4f1"' in fallback
        assert "font-family:'HowlMono','Departure Mono',monospace" in fallback
        assert "@font-face" not in fallback

    missing = json.loads(FIXTURE.read_text(encoding="utf-8"))
    missing["cards"] = [dict(missing["cards"][1], id="missing-asset", background_image="missing.webp")]
    with tempfile.TemporaryDirectory(prefix="howl-missing-asset-") as raw:
        bad = Path(raw) / "howl.json"
        bad.write_text(json.dumps(missing), encoding="utf-8")
        result = run([binary, "validate", "--manifest", str(bad)], check=False)
        assert result.returncode != 0 and "background_image not found" in result.stdout

    pairs = [
        ("#111111", "#ffffff"),
        ("#666666", "#ffffff"),
        ("#e6e6e6", "#0f1115"),
        ("#282828", "#ffffff"),
        ("#111111", "#f4f4f1"),
    ]
    for foreground, background in pairs:
        assert contrast(foreground, background) >= 4.5, f"contrast failed: {foreground} on {background}"


def fuzz_manifests(binary: str, count: int) -> None:
    rng = random.Random(110)
    malformed = ["", "{", "[", "null trailing", '{"cards":[}', '"unterminated']
    values: list[object] = [None, True, False, 0, 1, "text", [], {}, {"cards": []}, {"cards": "bad"}]
    alphabet: list[object] = [None, True, False, -1, 0, 1, "", "x", [], {}, ["x"], {"x": 1}]
    for _ in range(max(0, count - len(malformed) - len(values))):
        card = {key: rng.choice(alphabet) for key in rng.sample(["id", "title", "file", "concepts", "variant", "show_url", "transparent"], rng.randint(0, 7))}
        values.append({"project": rng.choice(alphabet), "cards": [card, rng.choice(alphabet)]})

    with tempfile.TemporaryDirectory(prefix="howl-manifest-fuzz-") as raw:
        root = Path(raw)
        cases = malformed + [json.dumps(value, ensure_ascii=False) for value in values]
        for index, payload in enumerate(cases[:count]):
            manifest = root / f"case-{index}.json"
            manifest.write_text(payload, encoding="utf-8")
            result = run([binary, "validate", "--manifest", str(manifest)], check=False)
            assert result.returncode != 0, f"invalid fuzz case {index} unexpectedly validated"
            combined = result.stdout + result.stderr
            assert "panic" not in combined.lower() and "index out of bounds" not in combined.lower(), f"fuzz case {index} crashed"


def verify_corpus(binary: str, label: str, manifest: Path) -> tuple[int, float, float, int | None]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    card_count = len(data.get("cards", []))
    with tempfile.TemporaryDirectory(prefix=f"howl-corpus-{label}-") as raw:
        base = Path(raw)
        a, b = base / "a", base / "b"
        run([binary, "validate", "--manifest", str(manifest)])
        started = time.perf_counter()
        run([binary, "render", "--manifest", str(manifest), "--out", str(a), "--format", "all"])
        cold = time.perf_counter() - started
        first = hashes(a)
        mtimes = {path: path.stat().st_mtime_ns for path in a.rglob("*") if path.is_file()}
        started = time.perf_counter()
        run([binary, "render", "--manifest", str(manifest), "--out", str(a), "--format", "all"])
        noop = time.perf_counter() - started
        assert mtimes == {path: path.stat().st_mtime_ns for path in a.rglob("*") if path.is_file()}, f"{label}: no-op rebuild rewrote files"
        run([binary, "render", "--manifest", str(manifest), "--out", str(b), "--format", "all"])
        assert first == hashes(b), f"{label}: output differs across clean renders"

        peak_rss = None
        time_tool = Path("/usr/bin/time")
        if time_tool.exists() and sys.platform == "darwin":
            measured = run([str(time_tool), "-l", binary, "render", "--manifest", str(manifest), "--out", str(base / "timed"), "--format", "all"])
            match = re.search(r"(\d+)\s+maximum resident set size", measured.stderr)
            if match:
                peak_rss = int(match.group(1))
    return card_count, cold, noop, peak_rss


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    assert data[:2] == b"\xff\xd8", "not a JPEG"
    offset = 2
    frames = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while offset + 8 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        if marker in frames:
            return int.from_bytes(data[offset + 7 : offset + 9], "big"), int.from_bytes(data[offset + 5 : offset + 7], "big")
        if marker in {0xD8, 0xD9}:
            offset += 2
            continue
        length = int.from_bytes(data[offset + 2 : offset + 4], "big")
        assert length >= 2, "invalid JPEG segment"
        offset += length + 2
    raise AssertionError("JPEG dimensions not found")


def verify_jpeg_pair(spec: str) -> str:
    label, manifest_raw, first_raw, second_raw = spec.split("=", 1)[0], *spec.split("=", 1)[1].split("::")
    manifest = json.loads(Path(manifest_raw).read_text(encoding="utf-8"))
    ids = {str(card["id"]) for card in manifest.get("cards", [])}
    first, second = Path(first_raw), Path(second_raw)
    for card_id in ids:
        a, b = first / f"{card_id}.jpg", second / f"{card_id}.jpg"
        assert a.exists() and b.exists(), f"{label}: missing JPEG for {card_id}"
        assert a.read_bytes() == b.read_bytes(), f"{label}: nondeterministic JPEG for {card_id}"
        assert jpeg_dimensions(a.read_bytes()) == (1200, 630), f"{label}: wrong JPEG dimensions for {card_id}"
    return f"{label}: {len(ids)} deterministic 1200x630 JPEGs"


def parse_pair(value: str) -> tuple[str, Path]:
    label, raw = value.split("=", 1)
    return label, Path(raw).resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--howl", default=os.environ.get("HOWL_BIN", str(ROOT / "bin" / "howl")))
    parser.add_argument("--site", action="append", default=[], metavar="LABEL=MANIFEST")
    parser.add_argument("--benchmark", metavar="LABEL=MANIFEST")
    parser.add_argument("--jpeg-pair", action="append", default=[], metavar="LABEL=MANIFEST::DIR_A::DIR_B")
    parser.add_argument("--fuzz-cases", type=int, default=64)
    parser.add_argument("--update-golden", action="store_true")
    args = parser.parse_args()

    binary = str(Path(args.howl).resolve())
    verify_fixture(binary, args.update_golden)
    fuzz_manifests(binary, args.fuzz_cases)
    reports = [f"fixture/golden/no-op/escaping/layout/contrast/fuzz: OK ({args.fuzz_cases} fuzz cases)"]
    benchmark_label = args.benchmark.split("=", 1)[0] if args.benchmark else None
    for raw in args.site:
        label, manifest = parse_pair(raw)
        count, cold, noop, peak = verify_corpus(binary, label, manifest)
        suffix = f", peak RSS {peak} bytes" if peak is not None and label == benchmark_label else ""
        reports.append(f"{label}: {count} cards, cold {cold:.3f}s, no-op {noop:.3f}s{suffix}")
    for raw in args.jpeg_pair:
        reports.append(verify_jpeg_pair(raw))
    print("\n".join(reports))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
