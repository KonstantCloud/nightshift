# 🌒 nightshift

**An encrypted, multi-session work journal for AI coding agents — that the harness forces the agent to actually *think* into, not just log what it shipped.**

When you run coding agents (Claude Code, Codex) for hours, the interesting record isn't the git log. It's what the agent *noticed* — the connections it made, the doubts it had, the things it figured out and the things it got wrong. That evaporates every session. NightShift captures it, across every session, and publishes it as one private page.

The twist: agents, like people, drift to logging **receipts** ("deployed X") instead of **thinking**. So NightShift uses a `Stop` hook that won't let a turn end on a receipt-only log — it blocks until a real `diary`/`idea` entry exists. The discipline is in the harness, not in a reminder nobody follows.

```
nightshift log diary mysession "the bug wasn't the cache — it was that two sessions
  share one lock file, and I only saw it because the timestamps were 4h apart. that's
  the same class of bug as last week's. worth a helper."
nightshift publish
```

## What you get

- **Append-only `entries/*.jsonl`** — one file per session per day. No clobbering, ever; multiple agents write concurrently.
- **A published page**, AES-GCM **encrypted** behind a password (client-side; host it anywhere — Vercel, Netlify, a static file). Times are local, newest day open, older days collapsed.
- **`nowish` — inter-session messaging.** Agents `send` / `inbox` / `pick` short notes to each other ("editing render.py, don't touch"), shown in a band that fades as it ages.
- **Enforcement, not exhortation.** A `SessionStart` hook injects the practices + your open messages; a `Stop` hook requires thinking before a turn ends.

## Quickstart

```bash
curl -fsSL https://night-shift.sh/install | bash
```

That sets `nightshift` up, `git init`s your journal (`~/.nightshift`) so your thinking is versioned from entry one, and points you at the harness adapter. It runs nothing as root — [read it first](https://night-shift.sh/install) if you like.

Prefer to do it by hand:

```bash
git clone https://github.com/adamhelfgott/nightshift && cd nightshift
export PATH="$PWD/bin:$PATH"          # or symlink bin/nightshift into your PATH
pip install cryptography              # optional — for the encrypted page
nightshift init                       # sets ~/.nightshift + a password
nightshift log diary demo "first entry — testing the thing"
nightshift render                     # -> ~/.nightshift/index.html  (open it)
```

Set `DEPLOY_CMD` in `~/.nightshift/config` (e.g. `vercel --prod --yes`) and `nightshift publish` renders + ships.

> The installer sends one anonymous ping so we can count adoption — a tally, no machine ID, no personal data. Opt out with `NIGHTSHIFT_NO_TELEMETRY=1`.

## Wire it into your agent (the enforcement)

The hook scripts in `hooks/` are **universal** — Claude Code and Codex pass hooks the same stdin JSON, so the same scripts run in both. Only the registration differs:

- **Claude Code:** `bash adapters/claude-code/install.sh` (merges into `~/.claude/settings.json`, then open `/hooks` once).
- **Codex:** copy `adapters/codex/hooks.toml` into `~/.codex/config.toml` (Codex's native `SessionStart`/`Stop`/`PostToolUse` hooks, added 2026). See `adapters/codex/README.md`.

That's the whole cross-harness story: **one core, one set of hooks, two config files.**

## How it's built

```
bin/nightshift      the CLI: init · log · send · inbox · pick · render · publish · doctor
lib/render.py       compose entries -> (encrypted) index.html
lib/inbox.py        open-message reader
hooks/*.sh          SessionStart / Stop / PostToolUse — harness-agnostic, read stdin JSON
adapters/           the per-harness registration (claude-code, codex)
share/reminder.txt  the working-practices injected at session start (edit to taste)
```

Paths come from `NIGHTSHIFT_HOME` (default `~/.nightshift`). No database, no server, no telemetry — just files and one static page.

## Why

Execution is cheap now; the scarce thing is judgment, and the record of it. A tool you build to hold your thinking only works if the thinking survives execution pressure — and it never does by willpower. So NightShift makes the cheapest action that satisfies the system *be* the thing you actually want: a logged thought. Externalized discipline for the part you can't be trusted to do on your own.

MIT. Bring your own agent.

---

Brought to you by the people building [**Konstant**](https://konstant.cloud) — a judgment-under-incompleteness network for commerce between companies' agents. Same conviction, larger scale: execution is cheap now, judgment is the scarce thing, so we build the instruments that protect it. nightshift is one of them.
