#!/usr/bin/env bash
# SessionStart: inject the working-practices reminder + any open inter-session messages.
NS="${NIGHTSHIFT_HOME:-$HOME/.nightshift}"
REM="${NIGHTSHIFT_REMINDER:-$NS/reminder.txt}"
ctx="$( [ -f "$REM" ] && cat "$REM" )"
# opt-in observation register (MIRROR=1 in config): invite observations about the human
if grep -qE '^MIRROR="?1"?' "$NS/config" 2>/dev/null; then ctx="$ctx

Also: when you notice something real about your human collaborator — a pattern, a blind spot, a call worth revisiting — log it with: nightshift observe <session> \"...\". It goes to a PRIVATE review inbox (nightshift mirror), never the shared page. It records; it does not act."
fi
# --brief truncates each note to ~140 chars; aging (NOWISH_TTL_HOURS) already dropped stale ones
inbox="$(NIGHTSHIFT_HOME="$NS" python3 "$(dirname "$0")/../lib/inbox.py" all --brief 2>/dev/null)"
# cap injection so even a burst of fresh notes can't bloat session context
n=$(printf '%s\n' "$inbox" | wc -l | tr -d ' ')
[ "$n" -gt 8 ] && inbox="$(printf '%s\n' "$inbox" | tail -8)
(…$((n-8)) more open — run: nightshift inbox)"
case "$inbox" in ""|"(inbox empty)"|"(no messages)") : ;; *) ctx="$ctx

OPEN INTER-SESSION MESSAGES (nowish) — claim yours: nightshift pick <id> <your-session>
$inbox" ;; esac
# calls past their due date: the agent chases the scoring, or nothing ever gets scored
NSBIN="$(cd "$(dirname "$0")/../bin" && pwd)/nightshift"
due="$(NIGHTSHIFT_HOME="$NS" "$NSBIN" due 2>/dev/null | head -8)"
case "$due" in ""|"(nothing due)") : ;; *) ctx="$ctx

CALLS DUE — your human made these predictions and reality has reported back. Ask how each resolved, then score it: nightshift score <id> right|wrong
$due" ;; esac
python3 -c "import json,sys;print(json.dumps({'hookSpecificOutput':{'hookEventName':'SessionStart','additionalContext':sys.stdin.read()}}))" <<<"$ctx"
