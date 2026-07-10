#!/usr/bin/env bash
# Merge NightShift hooks into ~/.claude/settings.json and seed the reminder.
set -euo pipefail
PKG="$(cd "$(dirname "$0")/../.." && pwd)"
NS="${NIGHTSHIFT_HOME:-$HOME/.nightshift}"
mkdir -p "$NS/entries"; cp -n "$PKG/share/reminder.txt" "$NS/reminder.txt" 2>/dev/null || true
S="$HOME/.claude/settings.json"; [ -f "$S" ] || echo '{}' > "$S"
SS="bash $PKG/hooks/session-start.sh"; PT="bash $PKG/hooks/posttool.sh"; ST="bash $PKG/hooks/stop.sh"
jq --arg ss "$SS" --arg pt "$PT" --arg st "$ST" '
  .hooks.SessionStart += [{"hooks":[{"type":"command","command":$ss,"timeout":10}]}] |
  .hooks.PostToolUse  += [{"matcher":"Bash","hooks":[{"type":"command","command":$pt,"timeout":10}]}] |
  .hooks.Stop         += [{"hooks":[{"type":"command","command":$st,"timeout":15}]}]' "$S" > "$S.tmp" && mv "$S.tmp" "$S"
echo "installed NightShift hooks into $S (PKG=$PKG). Open /hooks once to reload."
