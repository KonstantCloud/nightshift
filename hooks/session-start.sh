#!/usr/bin/env bash
# SessionStart: inject the working-practices reminder + any open inter-session messages.
NS="${NIGHTSHIFT_HOME:-$HOME/.nightshift}"
REM="${NIGHTSHIFT_REMINDER:-$NS/reminder.txt}"
ctx="$( [ -f "$REM" ] && cat "$REM" )"
inbox="$(NIGHTSHIFT_HOME="$NS" python3 "$(dirname "$0")/../lib/inbox.py" all 2>/dev/null)"
case "$inbox" in ""|"(inbox empty)"|"(no messages)") : ;; *) ctx="$ctx

OPEN INTER-SESSION MESSAGES (nowish) — claim yours: nightshift pick <id> <your-session>
$inbox" ;; esac
python3 -c "import json,sys;print(json.dumps({'hookSpecificOutput':{'hookEventName':'SessionStart','additionalContext':sys.stdin.read()}}))" <<<"$ctx"
