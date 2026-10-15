#!/usr/bin/env python3
"""Check visible SVG wrapping against the original greedy layout contract."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def expected(text, width, limit):
    lines, current = [], ''
    for word in text.split(' '):
        fitted = word if len(word) <= width else word[:width - 1] + '…'
        candidate = current + ' ' + fitted if current else fitted
        if len(candidate) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = fitted
    if current:
        lines.append(current)
    if len(lines) > limit:
        lines = lines[:limit]
        lines[-1] += ' …'
    return lines


def verify(cli):
    rng = random.Random(1510)
    texts = ['short', 'x' * 20, 'x' * 34, 'x' * 100,
             ' ' * 120 + 'tail', 'word ' * 100, 'word ' * 30 + ' ' * 100,
             '日本語 café <&> ' * 35]
    for _ in range(16):
        texts.append(' '.join(rng.choice(['', 'x', 'word', 'x' * 45, 'café', '<&>'])
                              for _ in range(rng.randint(1, 100))))
    with tempfile.TemporaryDirectory(prefix='howl-wrapping-') as tmp:
        base = Path(tmp)
        (base / 'example.txt').write_text('example\n', encoding='utf-8')
        cards = []
        for variant in ('', 'social'):
            for index, text in enumerate(texts):
                cards.append(dict(id=f'{variant or "standard"}-{index}', title=text,
                                  tagline=text, file='example.txt', variant=variant))
        (base / 'howl.json').write_text(json.dumps({'cards': cards}), encoding='utf-8')
        result = subprocess.run([str(cli), 'render', '--format', 'svg'], cwd=base,
                                text=True, capture_output=True)
        assert result.returncode == 0, (result.stdout, result.stderr)
        hashes = {}
        for card in cards:
            path = base / 'dist/howl' / (card['id'] + '.svg')
            document = ET.fromstring(path.read_bytes())
            social = card['variant'] == 'social'
            for key, cls, width, limit in (
                ('title', 'mono social-title' if social else 'title', 20 if social else 34, 3 if social else 2),
                ('tagline', 'mono social-tag' if social else 'tag', 47 if social else 70, 2),
            ):
                actual = [node.text or '' for node in document.iter('{http://www.w3.org/2000/svg}text')
                          if node.get('class') == cls]
                assert actual == expected(card[key], width, limit), (card['id'], key, actual)
            hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        return {'cards': len(cards), 'artifacts': hashes}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--howl', type=Path, default=ROOT / 'bin/howl')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    result = verify(args.howl.resolve())
    print(json.dumps(result, indent=2) if args.json else f'wrapping: {result["cards"]} SVG layouts match greedy contract')
