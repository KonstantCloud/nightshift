#!/usr/bin/env python3
"""Open (unpicked, unexpired) nowish messages for a session or 'all'.

A nowish note is ephemeral by design — a claim on a shared surface, a heads-up,
a handoff. It closes one of two ways: someone `pick`s it, or it ages out. Without
the second, the open pool grows without bound (sessions send far more than they
pick) and floods both the session-start injection and the page. So "open" means
unpicked AND newer than NOWISH_TTL_HOURS (config; default 12, 0 disables aging).
"""
import json, os, sys
from datetime import datetime

DEFAULT_TTL_HOURS = 12


def ttl_hours(home, key='NOWISH_TTL_HOURS', default=DEFAULT_TTL_HOURS):
    """Read a *_TTL_HOURS knob from $home/config. 0/negative = no aging."""
    cpath = os.path.join(home, 'config')
    if os.path.exists(cpath):
        for line in open(cpath, encoding='utf-8'):
            line = line.strip()
            if line.startswith(key):
                v = line.split('=', 1)[1].strip().strip('"').strip("'")
                try:
                    return float(v)
                except ValueError:
                    break
    return default


def age_hours(ts, now):
    """Hours between a local ts (`YYYY-MM-DDTHH:MM`, no tz) and now, or None if unparseable."""
    if not ts:
        return None
    try:
        t = datetime.fromisoformat(str(ts)[:16])
    except ValueError:
        return None
    return (now - t).total_seconds() / 3600.0


def open_messages(home, me='all', ttl=None):
    """Open nowish messages addressed to `me` (or all), newest last.

    Filters out picked ids and — when ttl > 0 — anything older than ttl hours.
    A message with an unparseable ts is kept (fail open: never hide on bad data).
    """
    path = os.path.join(home, 'nowish.jsonl')
    if not os.path.exists(path):
        return None
    if ttl is None:
        ttl = ttl_hours(home)
    now = datetime.now()
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
    out = []
    for i, m in msgs.items():
        if i in picked:
            continue
        if not (m.get('to') in (me, 'all') or me == 'all'):
            continue
        if ttl and ttl > 0:
            age = age_hours(m.get('ts', ''), now)
            if age is not None and age >= ttl:
                continue
        out.append(m)
    out.sort(key=lambda m: m.get('ts', ''))
    return out


def main(argv):
    args = [a for a in argv if not a.startswith('-')]
    brief = '--brief' in argv
    me = args[0] if args else 'all'
    home = os.environ.get('NIGHTSHIFT_HOME', os.path.expanduser('~/.nightshift'))
    o = open_messages(home, me)
    if o is None:
        print("(no messages)"); return
    if not o:
        print("(inbox empty)"); return
    lines = []
    for m in o:
        text = m.get('text', '')
        if brief and len(text) > 140:
            text = text[:137].rstrip() + '…'
        lines.append(f"{m['id']}  {m.get('ts','')}  {m.get('from','?')} -> {m.get('to','?')}: {text}")
    print("\n".join(lines))


if __name__ == '__main__':
    main(sys.argv[1:])
