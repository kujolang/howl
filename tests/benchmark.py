#!/usr/bin/env python3
"""Opt-in measured workload; no wall-clock thresholds in CI."""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--howl', type=Path, default=ROOT / 'bin/howl')
args = parser.parse_args()
cli = args.howl.resolve()
with tempfile.TemporaryDirectory(prefix='howl-benchmark-') as tmp:
    base = Path(tmp)
    (base / 'example.txt').write_text('print("hello")\n' * 50)
    (base / 'background.png').write_bytes(b'x' * 65536)
    cards = [dict(id=f'card-{i}', title='Benchmark', file='example.txt', variant='social', background_image='background.png') for i in range(8)]
    (base / 'howl.json').write_text(json.dumps({'cards': cards}))
    report = {'cards': 8, 'asset_bytes': 65536, 'samples': 5, 'commands': {}}
    for args in (['list'], ['caption', 'card-0'], ['show', 'card-0'], ['render', '--format', 'html']):
        times = []
        for _ in range(5):
            start = time.perf_counter()
            result = subprocess.run([str(cli), *args], cwd=base, capture_output=True)
            times.append(time.perf_counter() - start)
            assert result.returncode == 0, result.stderr
        report['commands'][' '.join(args)] = {'median_seconds': round(statistics.median(times), 6), 'stdout_bytes': len(result.stdout), 'seconds': times}
    print(json.dumps(report, indent=2))
