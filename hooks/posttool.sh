#!/usr/bin/env bash
# PostToolUse (Bash): arm the "did real work" sentinel on deploy/publish; clear on nightshift publish.
NS="${NIGHTSHIFT_HOME:-$HOME/.nightshift}"
CMD=$(cat | python3 -c "import json,sys;print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)
[ -z "$CMD" ] && exit 0
case "$CMD" in *nightshift*publish*|*nightshift*render*) rm -f "$NS/.pending" "$NS/.blocked" 2>/dev/null; exit 0;; esac
printf '%s' "$CMD" | grep -qE 'vercel (--prod|deploy)|git push|npm publish|nightshift log' && touch "$NS/.pending"
exit 0
