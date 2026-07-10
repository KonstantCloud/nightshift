#!/usr/bin/env python3
"""Print open (unpicked) nowish messages for a session or 'all'."""
import json, os, sys
me = sys.argv[1] if len(sys.argv) > 1 else 'all'
home = os.environ.get('NIGHTSHIFT_HOME', os.path.expanduser('~/.nightshift'))
path = os.path.join(home, 'nowish.jsonl')
if not os.path.exists(path):
    print("(no messages)"); sys.exit(0)
msgs, picked = {}, set()
for ln in open(path, encoding='utf-8'):
    ln = ln.strip()
    if not ln:
        continue
    try:
        r = json.loads(ln)
    except Exception:
        continue
    if not isinstance(r, dict) or r.get('id') is None:
        continue
    if r.get('kind') == 'msg':
        msgs[r['id']] = r
    elif r.get('kind') == 'pick':
        picked.add(r['id'])
o = [m for i, m in msgs.items() if i not in picked and (m.get('to') in (me, 'all') or me == 'all')]
o.sort(key=lambda m: m.get('ts', ''))
print("(inbox empty)" if not o else "\n".join(
    f"{m['id']}  {m.get('ts','')}  {m.get('from','?')} -> {m.get('to','?')}: {m.get('text','')}" for m in o))
