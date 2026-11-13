#!/usr/bin/env python3
"""Execute the exact short commands printed on the six tool cards."""
import argparse
from datetime import datetime, timezone
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading

C = Path(__file__).resolve().parents[1]
TOOLS = ['eval', 'workcell', 'packwrite', 'runledger', 'lens', 'shipcheck']

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--releases', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    releases, output = args.releases.resolve(), args.out.resolve()
    pins = json.loads((C / 'releases.json').read_text())
    runtime_hash = hashlib.sha256((releases / 'kujo').read_bytes()).hexdigest()
    assert subprocess.check_output([str(releases / 'kujo'), '--version'], text=True).strip() == 'kujo 1.9.0'
    output.mkdir(parents=True, exist_ok=False)
    # The URL shown on the card is also the URL we execute. Fail if occupied.
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 3000), functools.partial(QuietHandler, directory=str(C / 'inputs/site')))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    records = []
    try:
        for tool in TOOLS:
            dest = output / tool
            dest.mkdir()
            with tempfile.TemporaryDirectory(prefix='howl-short-commands-') as scratch:
                cwd = Path(scratch) / tool
                shutil.copytree(releases / (tool + '-source'), cwd, ignore=shutil.ignore_patterns('node_modules'))
                if tool == 'eval': shutil.copy(C / 'inputs/eval.json', cwd / 'eval.json')
                if tool == 'workcell': shutil.copy(C / 'inputs/workcell.json', cwd / 'workcell.json')
                if tool == 'packwrite':
                    shutil.copytree(C / 'inputs/agent', cwd / 'agent')
                    shutil.copy(C / 'inputs/packwrite.toml', cwd / 'packwrite.toml')
                if tool == 'lens':
                    shutil.copy(C / 'inputs/dashboard.json', cwd / 'dashboard.json')
                    (cwd / 'bridge/node_modules').symlink_to(releases / 'lens-source/bridge/node_modules', target_is_directory=True)
                env = dict(os.environ, KUJO=str(releases / 'kujo'), KUJO_BIN=str(releases / 'kujo'))
                env['PATH'] = str(cwd / 'bin') + os.pathsep + str(releases) + os.pathsep + env['PATH']
                env.pop('RUNLEDGER_DIR', None)
                for key in list(env):
                    if key.endswith('API_KEY') or key.startswith('PACKWRITE_FAKE_RESPONSE'): env.pop(key)
                setup = []
                if tool == 'workcell':
                    for command in [
                        ['git', 'init', '--quiet'],
                        ['git', 'add', 'workcell.json'],
                        ['git', '-c', 'user.name=Showcase Fixture', '-c', 'user.email=fixture@example.test', '-c', 'commit.gpgsign=false', 'commit', '--quiet', '-m', 'Workcell preflight fixture']
                    ]:
                        initialized = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=30)
                        assert initialized.returncode == 0, initialized.stderr
                        setup.append(dict(command=command, exit_code=initialized.returncode, stdout=initialized.stdout, stderr=initialized.stderr))
                if tool == 'runledger':
                    command = ['runledger', 'start', '--provider', 'local', '--model', 'demo', '--task', 'Showcase receipt', '--repo', '.']
                    start = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=30)
                    assert start.returncode == 0, start.stderr
                    setup.append(dict(command=command, exit_code=start.returncode, stdout=start.stdout, stderr=start.stderr))
                    env['id'] = next((cwd / '.runledger/runs').glob('*.json')).stem
                source = C / 'commands' / (tool + '.sh')
                command = ['bash', '-eux', str(source)]
                run = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=180)
                (dest / 'stdout.txt').write_text(run.stdout)
                (dest / 'stderr.txt').write_text(run.stderr)
                artifacts = dest / 'artifacts'
                artifacts.mkdir()
                assertion = run.returncode == 0
                if assertion and tool == 'eval':
                    shutil.copytree(cwd / 'eval-results', artifacts / 'eval-results')
                    result = json.loads((cwd / 'eval-results/last_run.json').read_text())
                    assertion = result['ok'] and result['data']['passed'] == 3 and result['data']['failed'] == 0
                elif assertion and tool == 'workcell':
                    result = json.loads(run.stdout.splitlines()[-1])
                    assertion = result['ok'] and result['policy']['network'] == 'none'
                elif assertion and tool == 'packwrite':
                    assertion = all(json.loads(line)['ok'] for line in run.stdout.splitlines())
                elif assertion and tool == 'runledger':
                    shutil.copytree(cwd / '.runledger', artifacts / 'ledger')
                    shutil.copy(cwd / 'run-report.md', artifacts / 'run-report.md')
                    assertion = json.loads(next((cwd / '.runledger/runs').glob('*.json')).read_text())['status'] == 'pass'
                elif assertion and tool == 'lens':
                    shutil.copytree(cwd / 'lens-results', artifacts / 'lens-results')
                    result = json.loads((cwd / 'lens-results/lens-report.json').read_text())
                    assertion = result['status'] == 'PASS' and result['summary']['checks_skipped'] == 0
                elif assertion and tool == 'shipcheck':
                    (artifacts / 'gate.json').write_text(run.stdout)
                    assertion = json.loads(run.stdout)['summary']['gate_passed'] == 1
                receipt = dict(id=tool, recorded_at_utc=datetime.now(timezone.utc).isoformat(), source=str(source.relative_to(C)), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), runtime_binary_sha256=runtime_hash, release=pins[tool], command=command, cwd=str(cwd), setup=setup, environment={k:env[k] for k in ['PATH','KUJO','KUJO_BIN']}, exit_code=run.returncode, assertions_passed=assertion, status='executed-successfully' if assertion else 'unverified')
                if tool == 'runledger': receipt['environment']['id'] = env['id']
                receipt['artifacts'] = [dict(path=str(p.relative_to(dest)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(artifacts.rglob('*')) if p.is_file()]
                (dest / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
                records.append(receipt)
                print(tool, receipt['status'], 'exit', run.returncode, flush=True)
    finally:
        server.shutdown(); server.server_close()
    (output / 'results.json').write_text(json.dumps(records, indent=2)+'\n')
    raise SystemExit(0 if all(r['assertions_passed'] for r in records) else 1)

if __name__ == '__main__': main()
