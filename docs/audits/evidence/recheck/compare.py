"""Compare this checkout with the immutable start of the September recheck.

Run from the Howl root with KUJO set. Downstream checkouts are read-only;
all archived source and rendered artifacts belong to an owned temp directory.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path.cwd()
START = '2a489084b8ebe5e1192eb7fdbaa3b3e19a52600e'
CORPORA = [ROOT / 'howl.json', ROOT / 'tests/fixtures/release/howl.json',
           ROOT.parent.parent.parent / 'robertdevore.com/howl.json',
           ROOT.parent.parent.parent / 'python.robertdevore.com/howl.json',
           ROOT.parent / 'kujolang.ai-work/howl-social.json',
           ROOT.parent / 'agents.kujolang.ai/howl.json']

def run(args, cwd):
    result = subprocess.run(args, cwd=cwd, capture_output=True)
    assert result.returncode == 0, (args, result.stdout, result.stderr)
    return result.stdout

with tempfile.TemporaryDirectory(prefix='howl-recheck-') as raw:
    work = Path(raw)
    before = work / 'before'
    before.mkdir()
    archive = run(['git', 'archive', START], ROOT)
    # The archive comes from this repository's recorded, trusted commit.
    subprocess.run(['tar', '-x', '-C', str(before)], input=archive, check=True)
    for index, manifest in enumerate(CORPORA):
        versions = []
        for label, cli in [('before', before / 'bin/howl'), ('after', ROOT / 'bin/howl')]:
            output = work / f'{index}-{label}'
            run([str(cli), 'render', '--manifest', str(manifest), '--out', str(output)], work)
            versions.append({p.name: (p.stat().st_size, hashlib.sha256(p.read_bytes()).hexdigest())
                             for p in output.iterdir()})
        assert versions[0] == versions[1], str(manifest)
        print(json.dumps({'manifest': str(manifest), 'cards': len(json.loads(manifest.read_text())['cards']),
                          'artifacts': len(versions[0]), 'bytes': sum(v[0] for v in versions[0].values()),
                          'byte_identical': True}), flush=True)
