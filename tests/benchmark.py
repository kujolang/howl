#!/usr/bin/env python3
"""Opt-in measured workload; no wall-clock thresholds in CI."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--howl', type=Path, default=ROOT / 'bin/howl')
parser.add_argument('--workload', choices=['metadata', 'unused-svg'], default='metadata')
args = parser.parse_args()
cli = args.howl.resolve()
with tempfile.TemporaryDirectory(prefix='howl-benchmark-') as tmp:
    base = Path(tmp)
    (base / 'example.txt').write_text('print("hello")\n' * 50)
    (base / 'background.png').write_bytes(b'x' * 65536)
    cards = [dict(id=f'card-{i}', title='Benchmark', file='example.txt', variant='social', background_image='background.png') for i in range(8)]
    commands = (['list'], ['caption', 'card-0'], ['show', 'card-0'], ['render', '--format', 'html'])
    if args.workload == 'unused-svg':
        for index, card in enumerate(cards):
            if index % 2:
                card['transparent'] = True
            else:
                card.pop('variant')
                card['font_file'] = 'background.png'
        commands = (['render', '--format', 'svg'], ['render', '--format', 'all'])
    (base / 'howl.json').write_text(json.dumps({'cards': cards}))
    report = {'workload': args.workload, 'cards': 8, 'asset_bytes': 65536, 'samples': 5, 'commands': {}}
    for args in commands:
        times = []
        for _ in range(5):
            start = time.perf_counter()
            result = subprocess.run([str(cli), *args], cwd=base, capture_output=True)
            times.append(time.perf_counter() - start)
            assert result.returncode == 0, result.stderr
        report['commands'][' '.join(args)] = {'median_seconds': round(statistics.median(times), 6), 'stdout_bytes': len(result.stdout), 'seconds': times}
    output = base / 'dist/howl'
    report['artifacts'] = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                           for p in sorted(output.glob('*')) if p.is_file()}
    print(json.dumps(report, indent=2))
