#!/usr/bin/env python3
"""Filesystem/CLI regression gate; all writes belong to one temporary tree."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'bin/howl'


def run(root, *args, cli=CLI):
    return subprocess.run([str(cli), *args], cwd=root, text=True, capture_output=True)


def verify():
    with tempfile.TemporaryDirectory(prefix='howl-hardening-') as tmp:
        root = Path(tmp)
        project = root / 'project'
        project.mkdir()
        (project / 'example.txt').write_text('example\n')
        card = {'id': 'example', 'title': 'Example', 'file': 'example.txt'}
        manifest = project / 'howl.json'

        def save(value):
            manifest.write_text(json.dumps({'cards': [value]}))

        def reject(*args):
            result = run(project, *args)
            assert result.returncode == 1, (args, result.returncode, result.stdout, result.stderr)
            assert 'howl:' in result.stdout + result.stderr, result
            return result

        save(card)
        (project / 'src').mkdir()
        (project / 'src/cli.kujo').write_text('export func main(argv) { print("SHADOWED"); return 0 }')
        result = run(project, 'validate')
        assert result.returncode == 0 and 'is valid' in result.stdout, result
        assert run(project, 'render').returncode == 0
        out = project / 'dist/howl'
        old = (out / 'example.md').read_bytes()
        (root / 'outside.txt').write_text('private sentinel')
        (project / 'escape.txt').symlink_to(root / 'outside.txt')
        for key in ('file', 'background_image', 'font_file'):
            save(dict(card, **{key: 'escape.txt'}))
            reject('validate')
            reject('render')
            assert (out / 'example.md').read_bytes() == old
        save(dict(card, file='.'))
        reject('validate')
        # Legitimate symlinks whose targets remain inside the manifest tree work.
        (project / 'inside.txt').symlink_to(project / 'example.txt')
        save(dict(card, file='inside.txt'))
        assert run(project, 'render').returncode == 0
        # index.html is the gallery, so the reserved card id must fail before writes.
        save(dict(card, id='index'))
        reject('validate')
        for prefix in ('\x00', '\x01', '\x08', '\x1f'):
            save(dict(card, url=prefix + 'javascript:alert(1)'))
            reject('validate')
        save(card)
        # A failed output must never print a success receipt or remove a directory.
        (out / 'example.md').unlink()
        (out / 'example.md').mkdir()
        (out / 'example.md/keep').write_text('keep')
        reject('render')
        assert (out / 'example.md/keep').read_text() == 'keep'
        (out / 'example.md/keep').unlink()
        (out / 'example.md').rmdir()
        (out / 'example.md').symlink_to(root / 'outside.txt')
        reject('render')
        assert (root / 'outside.txt').read_text() == 'private sentinel'
        (out / 'example.md').unlink()
        # Atomic failures preserve the prior artifact; no success receipt leaks.
        save(card)
        assert run(project, 'render').returncode == 0
        old = (out / 'example.md').read_bytes()
        save(dict(card, title='Changed title'))
        if os.geteuid() != 0:
            out.chmod(0o555)
            try:
                result = reject('render')
                assert 'rendered ' not in result.stdout
                assert (out / 'example.md').read_bytes() == old
            finally:
                out.chmod(0o755)
        assert run(project, 'render').returncode == 0
        new = (out / 'example.md').read_bytes()
        save(card)
        # A concurrent reader sees complete old/new files throughout replacement.
        process = subprocess.Popen([str(CLI), 'render'], cwd=project, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while process.poll() is None:
            assert (out / 'example.md').read_bytes() in (old, new)
        stdout, stderr = process.communicate()
        assert process.returncode == 0, (stdout, stderr)
        assert (out / 'example.md').read_bytes() == old
        assert not list(out.glob('.*.kujo-atomic-*.tmp'))
        # Markdown prose must stay text, and CR must not terminate a fence header.
        save(dict(card, title='[click](javascript:alert(1))', language='text\r<script>'))
        assert run(project, 'render').returncode == 0
        body = (out / 'example.md').read_bytes()
        assert b'[click](javascript:' not in body and b'\r' not in body
        (project / 'example.md').write_text('source must survive')
        save(dict(card, file='example.md'))
        reject('render', '--out', str(project))
        assert (project / 'example.md').read_text() == 'source must survive'
        assert not (project / 'example.html').exists()
        # Metadata and HTML commands must not read unused binary assets.
        with (project / 'large.png').open('wb') as asset:
            asset.truncate(9 * 1024 * 1024)
        save(dict(card, variant='social', background_image='large.png'))
        for args in [('list',), ('caption', 'example'), ('show', 'example'), ('render', '--format', 'html')]:
            result = run(project, *args)
            assert result.returncode == 0, (args, result.stdout, result.stderr)
        reject('render', '--format', 'svg')
        (project / 'invalid.txt').write_bytes(b'\xff')
        manifest.write_text(json.dumps({'cards': [card, dict(card, id='invalid', file='invalid.txt')]}))
        assert run(project, 'show', 'example').returncode == 0
        reject('show', 'invalid')
        # The documented PATH symlink installation preserves the caller's cwd.
        link = root / 'howl'
        link.symlink_to(CLI)
        save(card)
        result = run(project, 'validate', cli=link)
        assert result.returncode == 0, result.stderr
        print('hardening: containment, regular files, collisions, write failures, Markdown, launcher: OK')


if __name__ == '__main__':
    verify()
