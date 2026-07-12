#!/usr/bin/env bash
# Merge NightShift hooks into ~/.codex/hooks.json (Codex CLI's native hooks — same JSON
# shape and stdin contract as Claude Code, so the identical hooks/*.sh run unchanged).
# Idempotent: re-running replaces prior NightShift entries instead of duplicating them.
#
# IMPORTANT: Codex gates every new hook behind a one-time trust approval. After this
# script runs, open one interactive `codex` session and approve the three prompts —
# until you do, Codex silently skips them (by design; it's their consent mechanism).
set -euo pipefail
command -v jq >/dev/null 2>&1 || { echo "nightshift: jq is required (brew install jq / apt install jq)"; exit 1; }
PKG="$(cd "$(dirname "$0")/../.." && pwd)"
NS="${NIGHTSHIFT_HOME:-$HOME/.nightshift}"
mkdir -p "$NS/entries"; cp -n "$PKG/share/reminder.txt" "$NS/reminder.txt" 2>/dev/null || true
H="$HOME/.codex/hooks.json"
mkdir -p "$(dirname "$H")"; [ -f "$H" ] || echo '{"hooks":{}}' > "$H"
SS="bash \"$PKG/hooks/session-start.sh\""; PT="bash \"$PKG/hooks/posttool.sh\""; ST="bash \"$PKG/hooks/stop.sh\""
trap 'rm -f "$H.tmp"' EXIT
jq --arg ss "$SS" --arg pt "$PT" --arg st "$ST" '
  def strip(ev): [ (ev // [])[] | select( ([.hooks[]?.command // ""] | any(test("hooks/(session-start|posttool|stop)\\.sh"))) | not ) ];
  .hooks.SessionStart = strip(.hooks.SessionStart) + [{"hooks":[{"type":"command","command":$ss,"timeout":10}]}] |
  .hooks.PostToolUse  = strip(.hooks.PostToolUse)  + [{"matcher":"Bash","hooks":[{"type":"command","command":$pt,"timeout":10}]}] |
  .hooks.Stop         = strip(.hooks.Stop)         + [{"hooks":[{"type":"command","command":$st,"timeout":15}]}]' "$H" > "$H.tmp" && mv "$H.tmp" "$H"
echo "installed NightShift hooks into $H."
echo "LAST STEP (required once): open an interactive \`codex\` session and approve the three new hooks when prompted."
