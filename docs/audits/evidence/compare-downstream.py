import hashlib,json,os,subprocess,tempfile,difflib
from pathlib import Path
root=Path.cwd()
old=root/'.audit-local/before/bin/howl'
new=root/'bin/howl'
paths=[Path('/Users/robertdevore/2026/robertdevore.com/howl.json'),Path('/Users/robertdevore/2026/python.robertdevore.com/howl.json'),root.parent/'kujolang.ai-work/howl-social.json',root.parent/'agents.kujolang.ai/howl.json']
reports=[]
with tempfile.TemporaryDirectory(prefix='howl-compat-') as raw:
 work=Path(raw)
 for i,manifest in enumerate(paths):
  versions=[]
  for label,cli in [('before',old),('after',new)]:
   out=work/f'{i}-{label}'
   r=subprocess.run([str(cli),'render','--manifest',str(manifest),'--out',str(out)],cwd=work,capture_output=True,text=True)
   if r.returncode: raise RuntimeError(f'{manifest} {label}: {r.stdout}{r.stderr}')
   versions.append({p.name:p.read_bytes() for p in out.iterdir()})
  a,b=versions
  assert set(a)==set(b)
  diffs=[n for n in a if a[n]!=b[n]]
  assert all(n.endswith('.md') for n in diffs),diffs
  for n in diffs:
   with (root/'.audit-local/downstream-diffs.txt').open('a') as log:
    log.writelines(difflib.unified_diff(a[n].decode().splitlines(True),b[n].decode().splitlines(True),fromfile=str(manifest)+':'+n,tofile='after'))
  reports.append({'manifest':str(manifest),'cards':len(json.loads(manifest.read_text())['cards']),'files':len(a),'unchanged':len(a)-len(diffs),'changed_markdown':diffs})
  print(json.dumps(reports[-1]), flush=True)
