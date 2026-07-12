# Codex adapter

Codex CLI's native lifecycle hooks (`SessionStart` / `PostToolUse` / `Stop`, verified on
codex-cli 0.144) use the **same JSON registration shape and stdin contract as Claude Code**,
so the `hooks/*.sh` scripts run unchanged. Registration lives in `~/.codex/hooks.json`.

```bash
bash adapters/codex/install.sh
```

Then the one step no script can do for you: **open an interactive `codex` session and approve
the three new hooks when prompted.** Codex records a `trusted_hash` per hook in
`~/.codex/config.toml` and silently skips unapproved hooks (including in `codex exec`) — that's
its consent mechanism for code that runs every session, and it's a feature, not a bug.

Verify it took: start a session and ask the model "what working practices were injected at
session start?" — it should describe the nightshift reminder. Or check `[hooks.state]` in
`~/.codex/config.toml` for three new entries.

Notes:
- The Stop hook's block JSON (`{"decision":"block","reason":...}`) and SessionStart's
  `hookSpecificOutput.additionalContext` both follow the shared wire format.
- Older Codex builds used different registration; if `hooks.json` does nothing on your
  version, run `strings $(which codex) | grep SessionStart` to check support, and open an
  issue with your `codex --version`.
