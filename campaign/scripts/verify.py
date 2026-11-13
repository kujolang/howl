#!/usr/bin/env python3
"""Execute the twelve examples; retain commands, raw streams and artifacts."""
import argparse
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
from datetime import datetime, timezone

C = Path(__file__).resolve().parents[1]
BUILT = ['bounded-map', 'reusable-task', 'cancel-task', 'canonical-json', 'process-result', 'secret-output']
TOOLS = ['eval', 'workcell', 'packwrite', 'runledger', 'lens', 'shipcheck']
EXPECTED = {'bounded-map':'[2,4,6,8]\n', 'reusable-task':'42\nfalse\n', 'cancel-task':'true\ncancelled\n', 'canonical-json':'{"a":{"a":1,"b":2},"z":1}\ntrue\n', 'process-result':'ready\nfalse\nfalse\n', 'secret-output':'***\n{"api_key":"***"}\ntrue\n'}

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--releases', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True, help='New evidence directory; refuses to overwrite')
    parser.add_argument('--only', choices=BUILT + TOOLS, action='append')
    args = parser.parse_args()
    releases, out = args.releases.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    kujo = releases / 'kujo'
    version = subprocess.check_output([str(kujo), '--version'], text=True).strip()
    assert version == 'kujo 1.9.0', version
    pins = json.loads((C / 'releases.json').read_text())
    binary_hash = hashlib.sha256(kujo.read_bytes()).hexdigest()
    # Other platform binaries are accepted after bootstrap's official checksum verification.
    import platform
    if platform.system() == 'Darwin' and platform.machine() == 'x86_64':
        assert binary_hash == pins['kujo']['binary_sha256'], 'Unexpected runtime binary'
    env = dict(os.environ, KUJO=str(kujo), KUJO_BIN=str(kujo), RELEASES=str(releases), CAMPAIGN=str(C))
    # This campaign never invokes a provider or records credentials.
    for key in list(env):
        if key.endswith('API_KEY') or key.startswith('PACKWRITE_FAKE_RESPONSE'): del env[key]
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(C / 'inputs/site')))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    env['LENS_URL'] = f'http://127.0.0.1:{server.server_port}'
    records = []
    try:
        for name in args.only or BUILT + TOOLS:
            dest = out / name
            dest.mkdir()
            output = dest / 'artifacts'
            output.mkdir()
            env['OUTPUT'] = str(output)
            source = C / 'examples' / (name + ('.kujo' if name in BUILT else '.sh'))
            command = [str(kujo), 'run', str(source)] if name in BUILT else ['bash', '-x', str(source)]
            with tempfile.TemporaryDirectory(prefix='howl-example-') as scratch:
                work = Path(scratch)
                shutil.copy(C / 'inputs/kennel.toml', work)
                if name == 'packwrite':
                    shutil.copytree(C / 'inputs/agent', work / 'agent')
                    shutil.copy(C / 'inputs/packwrite.toml', work)
                started = datetime.now(timezone.utc).isoformat()
                try:
                    run = subprocess.run(command, cwd=work, env=env, text=True, capture_output=True, timeout=180)
                    stdout, stderr, code = run.stdout, run.stderr, run.returncode
                except subprocess.TimeoutExpired as exc:
                    stdout = exc.stdout or b''; stderr = exc.stderr or b''
                    stdout = stdout.decode() if isinstance(stdout, bytes) else stdout
                    stderr = stderr.decode() if isinstance(stderr, bytes) else stderr
                    stderr += '\nCampaign watchdog: timed out after 180s.\n'; code = 124
                (dest / 'stdout.txt').write_text(stdout)
                (dest / 'stderr.txt').write_text(stderr)
                assertion = stdout == EXPECTED[name] if name in BUILT else code == 0
                if name == 'eval' and code == 0:
                    report = json.loads((output / 'last_run.json').read_text())
                    assertion = report['ok'] and report['data']['failed'] == 0 and report['data']['passed'] == 3
                if name == 'workcell' and code == 0:
                    summary = json.loads(stdout.splitlines()[-1]); assertion = summary['ok'] and summary['policy']['network'] == 'none'
                if name == 'packwrite' and code == 0:
                    assertion = all(json.loads(line)['ok'] for line in stdout.splitlines())
                    shutil.copytree(work / 'agent', output / 'validated-pack')
                if name == 'lens' and code == 0:
                    report = json.loads((output / 'lens-report.json').read_text())
                    assertion = report['status'] == 'PASS' and report['viewports'] == ['desktop', 'mobile'] and report['summary']['checks_skipped'] == 0
                if name == 'runledger' and code == 0:
                    files = list((output / 'ledger/runs').glob('*.json'))
                    assertion = len(files) == 1 and json.loads(files[0].read_text())['status'] == 'pass'
                if name == 'shipcheck' and code == 0:
                    report = json.loads(stdout); (output / 'scan.json').write_text(stdout)
                    assertion = report['tool'] == 'shipcheck' and report['summary']['gate_passed'] == True
                record = {'id':name, 'started_at_utc':started, 'runtime':version,
                          'runtime_binary_sha256':binary_hash, 'command':command, 'cwd':scratch, 'source':str(source.relative_to(C)),
                          'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                          'exit_code':code, 'assertions_passed':assertion,
                          'status':'executed-successfully' if code == 0 and assertion else 'unverified',
                          'environment':{k:env[k] for k in ['KUJO','KUJO_BIN','RELEASES','CAMPAIGN','OUTPUT','LENS_URL']},
                          'artifacts':[]}
                record['artifacts'] = [{'path':str(p.relative_to(dest)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(output.rglob('*')) if p.is_file()]
                (dest / 'receipt.json').write_text(json.dumps(record, indent=2)+'\n')
                records.append(record)
                print(name, record['status'], 'exit', code, flush=True)
    finally:
        server.shutdown(); server.server_close()
    (out / 'results.json').write_text(json.dumps(records, indent=2)+'\n')
    raise SystemExit(0 if all(r['status']=='executed-successfully' for r in records) else 1)

if __name__ == '__main__': main()
