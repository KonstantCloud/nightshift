#!/usr/bin/env bash
# Merge NightShift hooks into ~/.claude/settings.json and seed the reminder.
# Idempotent: re-running replaces any prior NightShift entries instead of duplicating them.
set -euo pipefail
command -v jq >/dev/null 2>&1 || { echo "nightshift: jq is required for this step (brew install jq / apt install jq)"; exit 1; }
PKG="$(cd "$(dirname "$0")/../.." && pwd)"
NS="${NIGHTSHIFT_HOME:-$HOME/.nightshift}"
mkdir -p "$NS/entries"; cp -n "$PKG/share/reminder.txt" "$NS/reminder.txt" 2>/dev/null || true
S="$HOME/.claude/settings.json"
mkdir -p "$(dirname "$S")"; [ -f "$S" ] || echo '{}' > "$S"
SS="bash \"$PKG/hooks/session-start.sh\""; PT="bash \"$PKG/hooks/posttool.sh\""; ST="bash \"$PKG/hooks/stop.sh\""
trap 'rm -f "$S.tmp"' EXIT
jq --arg ss "$SS" --arg pt "$PT" --arg st "$ST" '
  def strip(ev): [ (ev // [])[] | select( ([.hooks[]?.command // ""] | any(test("hooks/(session-start|posttool|stop)\\.sh"))) | not ) ];
  .hooks.SessionStart = strip(.hooks.SessionStart) + [{"hooks":[{"type":"command","command":$ss,"timeout":10}]}] |
  .hooks.PostToolUse  = strip(.hooks.PostToolUse)  + [{"matcher":"Bash","hooks":[{"type":"command","command":$pt,"timeout":10}]}] |
  .hooks.Stop         = strip(.hooks.Stop)         + [{"hooks":[{"type":"command","command":$st,"timeout":15}]}]' "$S" > "$S.tmp" && mv "$S.tmp" "$S"
echo "installed NightShift hooks into $S. They load automatically in your NEXT session; for a session that's already running, open /hooks once to reload."
