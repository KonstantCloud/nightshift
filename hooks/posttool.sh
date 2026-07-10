#!/usr/bin/env bash
# PostToolUse (Bash): arm the "did real work" sentinel on deploy/publish/log.
# Sentinels are keyed per session so concurrent agents never block each other.
# Deliberately does NOT clear on `nightshift publish` — only logged thinking clears (see stop.sh).
NS="${NIGHTSHIFT_HOME:-$HOME/.nightshift}"
IN=$(cat)
CMD=$(printf '%s' "$IN" | python3 -c "import json,sys;print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)
SID=$(printf '%s' "$IN" | python3 -c "import json,sys;print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null)
[ -z "$CMD" ] && exit 0
SUF=${SID:+.$SID}
printf '%s' "$CMD" | grep -qE 'vercel (--prod|deploy)|git push|npm publish|nightshift log' && touch "$NS/.pending$SUF" 2>/dev/null
exit 0
