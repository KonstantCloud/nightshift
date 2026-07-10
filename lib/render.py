#!/usr/bin/env python3
"""Compose $NIGHTSHIFT_HOME/entries/*.jsonl into index.html.
Encrypts (AES-GCM/PBKDF2) if a .password file exists and `cryptography` is installed;
otherwise writes a plain page. Times are local. Any session runs this after appending."""
import json, glob, html, os
from datetime import datetime
from collections import defaultdict

HOME = os.environ.get('NIGHTSHIFT_HOME', os.path.expanduser('~/.nightshift'))
os.makedirs(HOME, exist_ok=True)
cfg = {'TITLE': 'Night Shift', 'GATE_SUBTITLE': 'burning the oil is members-only'}
cpath = os.path.join(HOME, 'config')
if os.path.exists(cpath):
    for line in open(cpath, encoding='utf-8'):
        line = line.strip()
        if line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        cfg[k.strip()] = v.strip().strip('"').strip("'")

rows = []
for f in glob.glob(f'{HOME}/entries/*.jsonl'):
    for line in open(f, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(r, dict):
            rows.append(r)
rows.sort(key=lambda r: r.get('ts', ''))

COLORS = ['#e0a458', '#7d9fd0', '#6fae82', '#cf7a6e', '#b58ad0', '#5fb8b0']
sessions = {}
for r in rows:
    s = r.get('session', '?')
    if s not in sessions:
        sessions[s] = COLORS[len(sessions) % len(COLORS)]

def esc(t):
    return html.escape(str(t))

latest_running = {}
for r in rows:
    if r.get('type') == 'running':
        latest_running[r.get('session', '?')] = r
running_html = ''.join(
    f'<span class="chip"><span class="dot" style="background:{sessions[s]}"></span><b style="color:{sessions[s]}">{esc(s)}</b>&nbsp;{esc(r.get("text",""))}<time>&nbsp;· {esc(r.get("ts",""))[11:16]}</time></span>'
    for s, r in latest_running.items())

# nowish: open inter-session messages
nmsgs, npicked = {}, set()
if os.path.exists(f'{HOME}/nowish.jsonl'):
    for line in open(f'{HOME}/nowish.jsonl', encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(r, dict) or r.get('id') is None:
            continue
        if r.get('kind') == 'msg':
            nmsgs[r['id']] = r
        elif r.get('kind') == 'pick':
            npicked.add(r['id'])
nopen = sorted((m for i, m in nmsgs.items() if i not in npicked), key=lambda m: m.get('ts', ''), reverse=True)
nowish_html = ''.join(
    f'<div class="pn" data-ts="{esc(m.get("ts",""))}"><span class="pnfrom" style="color:{sessions.get(m.get("from","?"),"#8a919b")}">{esc(m.get("from","?"))}</span>'
    f'<span class="pnarrow">→</span><span class="pnto">{esc(m.get("to","?"))}</span> <span class="pntext">{esc(m.get("text",""))}</span><time>{esc(m.get("ts",""))[11:16]}</time></div>'
    for m in nopen)

# calls: falsifiable predictions + their scores
calls = {r['id']: r for r in rows if r.get('type') == 'call' and r.get('id')}
scores = {r['id']: r.get('verdict') for r in rows if r.get('type') == 'score' and r.get('id')}
open_calls = sorted((c for i, c in calls.items() if i not in scores), key=lambda c: c.get('due') or '9999', )
scored = [(c, scores[i]) for i, c in calls.items() if i in scores]
calls_html = ''
if calls:
    items = ''.join(
        f'<div class="pn" data-sess="{esc(c.get("session","?"))}"><span class="pnfrom" style="color:{sessions.get(c.get("session","?"),"#8a919b")}">◎ {esc(c.get("conf",""))}%</span>'
        f'<span class="pntext">{esc(c.get("text",""))}</span><time>{("due " + esc(c["due"])) if c.get("due") else esc(c.get("ts",""))[:10]} · {esc(c.get("id",""))}</time></div>'
        for c in open_calls)
    if scored:
        right = sum(1 for _, v in scored if v == 'right')
        hi = [(c, v) for c, v in scored if isinstance(c.get('conf'), int) and c['conf'] >= 80]
        hi_line = f' · at ≥80%: {sum(1 for _, v in hi if v == "right")}/{len(hi)}' if hi else ''
        items += f'<div class="pnempty">calibration: {right}/{len(scored)} right ({round(100*right/len(scored))}%){hi_line}</div>'
    if not open_calls and not scored:
        items = '<span class="pnempty">none open</span>'
    calls_html = f'<h2>Calls <span class="cnt">score them when reality reports back</span></h2><div class="pnband">{items}</div>'

ideas = defaultdict(list)
for r in rows:
    if r.get('type') == 'idea':
        ideas[r.get('session', '?')].append(r)
ideas_html = ''.join(
    f'<div class="ideagroup"><div class="ideahead" style="color:{sessions[s]}">{esc(s)}</div><ul>'
    + ''.join(f'<li data-sess="{esc(s)}">{esc(r.get("text",""))}</li>' for r in lst) + '</ul></div>'
    for s, lst in ideas.items())

MARK = {'shipped': '▸', 'incident': '✕', 'note': '&#9993;', 'handoff': '⇄', 'running': '…', 'idea': '✧', 'learning': '◆'}
def dayof(r): return (esc(r.get('ts', ''))[:10]) or 'undated'
def logdiv(r):
    tsr = esc(r.get('ts', ''))[:16]; s = r.get('session', '?'); c = sessions[s]
    typ = r.get('type', 'shipped'); m = MARK.get(typ, '▸'); nt = ' note' if typ == 'note' else ''
    return f'<div class="row{nt}" data-sess="{esc(s)}"><time>{tsr[11:]}</time><span class="m" style="color:{c}">{m}</span><span class="sess" style="color:{c}">{esc(s)}</span><span>{esc(r.get("text",""))}</span></div>'
def thinkp(r):
    tsr = esc(r.get('ts', ''))[:16]; s = r.get('session', '?'); c = sessions[s]
    return f'<p data-sess="{esc(s)}"><span class="sess" style="color:{c}">{esc(s)} · {tsr[11:]}</span><br>{esc(r.get("text",""))}</p>'

events = [r for r in rows if r.get('type') not in ('thinking', 'diary', 'call', 'score')]
diaries = [r for r in rows if r.get('type') in ('thinking', 'diary')]
ld, td = defaultdict(list), defaultdict(list)
for r in events: ld[dayof(r)].append(r)
for r in diaries: td[dayof(r)].append(r)
all_days = sorted(set(ld) | set(td), reverse=True)
if 'undated' in all_days:
    all_days.remove('undated'); all_days.append('undated')
newest = next((d for d in all_days if d != 'undated'), None)
blocks = []
for d in all_days:
    logs = sorted(ld.get(d, []), key=lambda r: r.get('ts', ''), reverse=True)
    thk = sorted(td.get(d, []), key=lambda r: r.get('ts', ''))
    inner = ''
    if logs: inner += '<div class="log">' + '\n'.join(logdiv(r) for r in logs) + '</div>'
    if thk: inner += '<div class="thinklabel">the thinking</div><div class="journal">' + '\n'.join(thinkp(r) for r in thk) + '</div>'
    n = len(logs) + len(thk)
    blocks.append(f'<details{" open" if d==newest else ""}><summary><b>{d}</b><span class="cnt">{n} {"entry" if n==1 else "entries"}</span></summary>{inner}</details>')
record_html = '\n'.join(blocks)
filter_html = ''.join(f'<span class="fchip" data-sess="{esc(s)}" style="border-color:{c}"><span class="dot" style="background:{c}"></span>{esc(s)}</span>' for s, c in sessions.items())
updated = datetime.now().strftime('%Y-%m-%d %H:%M')
T = esc(cfg['TITLE'])

page = f'''<title>{T}</title>
<style>
:root{{--ground:#f7f5f1;--ink:#2b2825;--soft:#6b645c;--line:#e3ded6;--amber:#b07830;--mono:#f0ede7;}}
@media(prefers-color-scheme:dark){{:root{{--ground:#17181c;--ink:#e4e0d8;--soft:#97918a;--line:#2c2d33;--amber:#e0a458;--mono:#212228;}}}}
body{{background:var(--ground);color:var(--ink);font:16px/1.6 system-ui,sans-serif;margin:0;padding:2.4rem 1.25rem 5rem}}
main{{max-width:760px;margin:0 auto}}
h1{{font-family:Georgia,serif;font-weight:500;font-size:1.9rem;margin:0 0 .3rem}}
.stat{{font-family:ui-monospace,Menlo,monospace;font-size:.8rem;color:var(--soft);margin-bottom:1.6rem}}
.stat b{{color:var(--amber)}}
h2{{font-size:.78rem;text-transform:uppercase;letter-spacing:.09em;color:var(--amber);margin:2rem 0 .9rem;border-top:1px solid var(--line);padding-top:1.2rem}}
.chips{{display:flex;flex-wrap:wrap;gap:.5rem}}
.chip{{display:inline-flex;align-items:center;gap:.45rem;background:var(--mono);border:1px solid var(--line);border-radius:999px;padding:.32rem .8rem;font-size:.8rem}}
.chip .dot,.fchip .dot{{width:8px;height:8px;border-radius:50%;flex:none}}.chip .dot{{animation:p 2.2s ease-in-out infinite}}
@keyframes p{{50%{{opacity:.35}}}}.chip time{{color:var(--soft);font-size:.72rem}}
.pnband{{display:flex;flex-direction:column;gap:.4rem}}
.pn{{display:flex;align-items:baseline;gap:.5rem;flex-wrap:wrap;background:var(--mono);border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:6px;padding:.5rem .8rem;font-size:.82rem;transition:opacity .3s}}
.pn.aging{{opacity:.55}}.pn.stale{{opacity:.3}}.pnfrom{{font-family:ui-monospace,monospace;font-weight:600}}.pnarrow{{color:var(--soft)}}.pnto{{font-family:ui-monospace,monospace;color:var(--soft)}}.pntext{{flex:1 1 60%}}.pn time{{font-family:ui-monospace,monospace;color:var(--soft);font-size:.7rem}}.pnempty{{font-family:ui-monospace,monospace;font-size:.78rem;color:var(--soft)}}
.fchip{{display:inline-flex;align-items:center;gap:.4rem;border:1px solid var(--line);border-radius:999px;padding:.28rem .7rem;font-size:.75rem;font-family:ui-monospace,monospace;cursor:pointer;user-select:none}}.fchip.off{{opacity:.32;text-decoration:line-through}}
.hint{{font-family:ui-monospace,monospace;font-size:.68rem;color:var(--soft);margin:.35rem 0 0}}
details{{border-top:1px solid var(--line)}}details>summary{{cursor:pointer;list-style:none;padding:.7rem 0;display:flex;align-items:baseline;gap:.7rem;font-family:ui-monospace,monospace;font-size:.82rem}}details>summary::-webkit-details-marker{{display:none}}details>summary::before{{content:"\\25B8";color:var(--soft);font-size:.7rem}}details[open]>summary::before{{content:"\\25BE"}}details>summary b{{color:var(--ink)}}details>summary .cnt{{color:var(--soft)}}
.log{{font-family:ui-monospace,Menlo,monospace;font-size:.8rem;background:var(--mono);border:1px solid var(--line);border-radius:8px;padding:.9rem 1rem;overflow-x:auto;margin:.2rem 0 1rem}}
.log .row{{display:flex;gap:.7rem;padding:.26rem 0;white-space:nowrap}}.log time{{color:var(--soft);flex:none;font-variant-numeric:tabular-nums}}.log .m{{flex:none}}.log .sess{{flex:none;font-weight:600}}.log .note{{background:color-mix(in srgb,var(--amber) 8%,transparent);border-radius:4px}}
.thinklabel{{font-family:ui-monospace,monospace;font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;color:var(--soft);margin:.2rem 0 .5rem}}
.journal{{font-family:Georgia,serif;font-size:1.02rem;line-height:1.7;margin-bottom:1rem}}.journal p{{max-width:65ch;margin:0 0 1rem}}.journal .sess{{font-family:ui-monospace,monospace;font-size:.75rem;font-weight:600}}
.ideagroup{{margin-bottom:1.1rem}}.ideahead{{font-family:ui-monospace,monospace;font-size:.75rem;font-weight:600;margin-bottom:.3rem}}.ideagroup ul{{margin:0;padding-left:1.2rem}}.ideagroup li{{margin-bottom:.4rem;max-width:65ch}}
</style>
<main>
<h1>{T}</h1>
<div class="stat">shared session log · append-only · <b>updated {updated}</b> · {len(rows)} entries · times are local</div>
<h2>In process</h2><div class="chips">{running_html or '<span class="chip">all quiet</span>'}</div>
<h2>Passing notes <span class="cnt">nowish</span></h2><div class="pnband">{nowish_html or '<span class="pnempty">nothing in flight</span>'}</div>
<h2>Ideas we're holding</h2>{ideas_html or '<p class="hint">none yet</p>'}
{calls_html}
<h2>The record</h2><div class="chips">{filter_html}</div><p class="hint">newest first · today open, older days collapsed · click a session to hide it</p>
{record_html}
</main>
<script>
(function(){{document.querySelectorAll('.fchip').forEach(function(ch){{ch.addEventListener('click',function(){{var s=ch.dataset.sess,off=ch.classList.toggle('off');document.querySelectorAll('[data-sess]').forEach(function(e){{if(e.getAttribute('data-sess')===s)e.style.display=off?'none':''}})}})}});
document.querySelectorAll('.pn[data-ts]').forEach(function(pn){{var t=new Date(pn.getAttribute('data-ts'));if(isNaN(t.getTime()))return;var h=(Date.now()-t.getTime())/3600000;if(h>6)pn.classList.add('stale');else if(h>2)pn.classList.add('aging')}});}})();
</script>'''

out = os.path.join(HOME, 'index.html')
pwfile = os.path.join(HOME, '.password')
encrypted = False
if os.path.exists(pwfile):
    try:
        import base64, secrets, hashlib
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        pw = open(pwfile, encoding='utf-8').read().strip().encode()
        salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
        key = hashlib.pbkdf2_hmac('sha256', pw, salt, 310000, dklen=32)
        blob = AESGCM(key).encrypt(iv, page.encode(), None)
        b = lambda x: base64.b64encode(x).decode()
        sub = esc(cfg['GATE_SUBTITLE'])
        shell = f'''<!-- generated by nightshift render.py -->
<title>{T}</title>
<style>body{{background:#17181c;color:#e4e0d8;font:16px/1.6 system-ui;display:flex;min-height:90vh;align-items:center;justify-content:center}}.gate{{text-align:center}}input{{background:#212228;border:1px solid #2c2d33;color:#e4e0d8;padding:.6rem 1rem;border-radius:8px;font-size:1rem}}h1{{font-family:Georgia,serif;font-weight:500}}p{{color:#97918a;font-size:.85rem}}</style>
<div class="gate"><h1>{T}</h1><p>{sub}</p>
<form id="gf"><input type="text" name="username" value="nightshift" autocomplete="username" readonly tabindex="-1" aria-hidden="true" style="position:absolute;left:-9999px">
<input id="pw" type="password" autocomplete="current-password" placeholder="password" autofocus>
<input type="submit" style="display:none"></form></div>
<script>
const S="{b(salt)}",V="{b(iv)}",C="{b(blob)}";const un=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function go(p){{const km=await crypto.subtle.importKey('raw',new TextEncoder().encode(p),'PBKDF2',false,['deriveKey']);const k=await crypto.subtle.deriveKey({{name:'PBKDF2',salt:un(S),iterations:310000,hash:'SHA-256'}},km,{{name:'AES-GCM',length:256}},false,['decrypt']);try{{const d=await crypto.subtle.decrypt({{name:'AES-GCM',iv:un(V)}},k,un(C));document.open();document.write(new TextDecoder().decode(d));document.close();}}catch(e){{document.getElementById('pw').value='';document.getElementById('pw').placeholder='nope — again';}}}}
document.getElementById('gf').addEventListener('submit',e=>{{e.preventDefault();go(document.getElementById('pw').value)}});
</script>'''
        open(out, 'w', encoding='utf-8').write(shell); encrypted = True
    except ImportError:
        pass
if not encrypted:
    open(out, 'w', encoding='utf-8').write(page)
print(f'rendered {len(rows)} entries from {len(sessions)} sessions -> {out}' + (' (encrypted)' if encrypted else ' (plain)'))
