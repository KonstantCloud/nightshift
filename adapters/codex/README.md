# Codex adapter

Codex CLI (2026+) has native lifecycle hooks whose event names and stdin JSON match Claude Code, so the
`hooks/*.sh` scripts run unchanged. Only the registration format differs.

1. `cp share/reminder.txt ~/.nightshift/reminder.txt`
2. Copy the tables in `hooks.toml` into `~/.codex/config.toml` (replace `<PKG>` with this repo's absolute path),
   or put them in `~/.codex/hooks.json` in the equivalent JSON shape.
3. Instructions: add a pointer to `nightshift log` in your `AGENTS.md` so the model knows the convention.

Notes: Codex's `Stop` hook receives `last_assistant_message` on stdin; `notify` (config.toml) is a coarser
turn-complete alternative if you can't use hooks. The `additionalContext` injection on SessionStart follows the
same `hookSpecificOutput` shape — verify against your Codex version and adjust `session-start.sh`'s final line if needed.
