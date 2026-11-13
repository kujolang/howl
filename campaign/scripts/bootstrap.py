#!/usr/bin/env python3
"""Fetch pinned public releases into a new directory; never installs globally."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import tarfile

C = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--destination', type=Path, required=True)
args = parser.parse_args()
dest = args.destination.resolve()
dest.mkdir(parents=True, exist_ok=False)
releases = json.loads((C / 'releases.json').read_text())
def run(*args, **kwargs): subprocess.run(args, check=True, **kwargs)
for name, pin in releases.items():
    target = dest / (name + '-source')
    run('git', 'clone', '--quiet', '--depth', '1', '--branch', pin['tag'], f'https://github.com/kujolang/{name}.git', str(target))
    commit = subprocess.check_output(['git', '-C', str(target), 'rev-parse', 'HEAD'], text=True).strip()
    assert commit == pin['commit'], f'Release commit changed: {name}'
system = {'Darwin':'macos','Linux':'linux'}.get(platform.system())
arch = {'x86_64':'x64','amd64':'x64','arm64':'arm64','aarch64':'arm64'}.get(platform.machine().lower())
if not system or not arch: raise SystemExit('This bootstrap supports macOS/Linux x64/arm64.')
archive_name = f'kujo-v1.9.0-{system}-{arch}.tar.gz'
run('gh', 'release', 'download', 'v1.9.0', '--repo', 'kujolang/kujo', '--pattern', archive_name+'*', '--dir', str(dest))
archive = dest / archive_name
expected = Path(str(archive)+'.sha256').read_text().split()[0]
actual = hashlib.sha256(archive.read_bytes()).hexdigest()
assert actual == expected, 'Official archive checksum mismatch'
if archive_name == releases['kujo']['archive']: assert actual == releases['kujo']['archive_sha256']
with tarfile.open(archive) as package:
    for member in package.getmembers():
        target = (dest / member.name).resolve()
        assert dest in target.parents and not member.issym() and not member.islnk(), 'Unsafe archive path'
    package.extractall(dest)
run(str(dest / 'kujo'), '--version')
run('npm', 'ci', '--ignore-scripts', cwd=dest / 'lens-source/bridge')
run('npm', 'run', 'install-browser', cwd=dest / 'lens-source/bridge')
print('Ready:', dest)
