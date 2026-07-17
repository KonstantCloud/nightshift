#!/usr/bin/env python3
"""Merge orphan nightshift stores into the home store (append-only, deduped).

Sandboxed agents that can't reach the real NIGHTSHIFT_HOME fall back to a
repo-local home (e.g. ./.cache/nightshift*), and that thinking never rejoins the
journal. `sync` heals that: point it at one or more orphan homes and it appends
their entries and observations into the home store, skipping any line already
there. Idempotent — running twice adds nothing the second time. nowish notes are
ephemeral coordination and are NOT merged unless --nowish is passed.
"""
import glob, os, sys

HOME = os.environ.get('NIGHTSHIFT_HOME', os.path.expanduser('~/.nightshift'))


def _merge_file(src, dst):
    """Append lines of src not already present in dst. Returns lines added."""
    if not os.path.exists(src):
        return 0
    existing = set()
    if os.path.exists(dst):
        for ln in open(dst, encoding='utf-8'):
            existing.add(ln.rstrip('\n'))
    add = []
    for ln in open(src, encoding='utf-8'):
        s = ln.rstrip('\n')
        if s and s not in existing:
            existing.add(s)
            add.append(s)
    if add:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'a', encoding='utf-8') as f:
            for s in add:
                f.write(s + '\n')
    return len(add)


def sync_home(orphan, want_nowish=False):
    orphan = os.path.abspath(orphan)
    if orphan == os.path.abspath(HOME):
        return None  # never merge home into itself
    ent_added = files = 0
    for src in sorted(glob.glob(os.path.join(orphan, 'entries', '*.jsonl'))):
        n = _merge_file(src, os.path.join(HOME, 'entries', os.path.basename(src)))
        if n:
            files += 1
            ent_added += n
    obs_added = _merge_file(os.path.join(orphan, 'observations.jsonl'),
                            os.path.join(HOME, 'observations.jsonl'))
    now_added = 0
    if want_nowish:
        now_added = _merge_file(os.path.join(orphan, 'nowish.jsonl'),
                                os.path.join(HOME, 'nowish.jsonl'))
    return {'orphan': orphan, 'entry_files': files, 'entries': ent_added,
            'observations': obs_added, 'nowish': now_added}


def main(argv):
    want_nowish = '--nowish' in argv
    dirs = [a for a in argv if not a.startswith('-')]
    if not dirs:
        print("usage: nightshift sync <orphan-home> [<orphan-home>...] [--nowish]")
        print("  merges a sandbox/fallback store's entries + observations into", HOME)
        return 1
    tot = {'entry_files': 0, 'entries': 0, 'observations': 0, 'nowish': 0}
    for d in dirs:
        r = sync_home(d, want_nowish)
        if r is None:
            print(f"skip {d} (is the home store)"); continue
        for k in tot:
            tot[k] += r[k]
        print(f"{d}: +{r['entries']} entries across {r['entry_files']} files, "
              f"+{r['observations']} observations" + (f", +{r['nowish']} nowish" if want_nowish else ""))
    print(f"\nmerged: +{tot['entries']} entries, +{tot['observations']} observations"
          + (f", +{tot['nowish']} nowish" if want_nowish else "")
          + f"  → run `nightshift publish` to render them onto the page")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
