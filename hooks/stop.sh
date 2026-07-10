#!/usr/bin/env bash
# Stop: a ship/turn only clears once THINKING (a diary/idea entry) exists in the last 30 min — not a bare receipt.
NS="${NIGHTSHIFT_HOME:-$HOME/.nightshift}"
[ -f "$NS/.pending" ] || exit 0
THINK=$(NIGHTSHIFT_HOME="$NS" python3 - <<'PY' 2>/dev/null
import json,glob,os,time,datetime
now=time.time();hit=0
for f in glob.glob(os.path.join(os.environ['NIGHTSHIFT_HOME'],'entries','*.jsonl')):
    try:
        for ln in open(f):
            ln=ln.strip()
            if not ln:continue
            try:r=json.loads(ln)
            except:continue
            if r.get('type') in ('diary','idea'):
                try:
                    if now-datetime.datetime.strptime(r.get('ts','')[:16],'%Y-%m-%dT%H:%M').timestamp()<1800:hit=1
                except:pass
    except:pass
print(hit)
PY
)
if [ "$THINK" = "1" ]; then rm -f "$NS/.pending" "$NS/.blocked" 2>/dev/null; exit 0; fi
if [ -f "$NS/.blocked" ]; then rm -f "$NS/.blocked"; exit 0; fi
touch "$NS/.blocked"
printf '{"decision":"block","reason":"You did work this turn but only a RECEIPT is logged, not your thinking. Add a diary or idea entry (a real connection, doubt, or noticing): nightshift log diary <session> \\"...\\"  then: nightshift publish. A shipped/running line alone does not count."}'
exit 0
