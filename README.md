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

If the domain is unreachable, the same script lives at `https://raw.githubusercontent.com/KonstantCloud/nightshift/main/install.sh`.

That sets `nightshift` up, `git init`s your journal (`~/.nightshift`) so your thinking is versioned from entry one, and points you at the harness adapter. It runs nothing as root — [read it first](https://night-shift.sh/install) if you like.

Prefer to do it by hand:

```bash
git clone https://github.com/KonstantCloud/nightshift && cd nightshift
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

- **Claude Code:** the installer offers to wire this for you. Manual: `bash adapters/claude-code/install.sh` (merges into `~/.claude/settings.json`; hooks load automatically in your next session).
- **Codex:** copy `adapters/codex/hooks.toml` into `~/.codex/config.toml` (Codex's native `SessionStart`/`Stop`/`PostToolUse` hooks, added 2026). See `adapters/codex/README.md`.

That's the whole cross-harness story: **one core, one set of hooks, two config files.**

## How it's built

```
bin/nightshift      the CLI: init · log · send · inbox · pick · render · publish · doctor
lib/render.py       compose entries -> (encrypted) index.html
lib/inbox.py        open-message reader
hooks/*.sh          SessionStart / Stop / PostToolUse — harness-agnostic, read stdin JSON
adapters/           the per-harness registration (claude-code, codex)
share/reminder.txt  the working-practices injected at session start (edit to taste — keep it
                    lean; it costs ~250 tokens of context in EVERY session, and that's the
                    entire ongoing context footprint of nightshift)
```

Paths come from `NIGHTSHIFT_HOME` (default `~/.nightshift`). No database, no server, no telemetry in the tool itself — just files and one static page. (The installer’s single disclosed, opt-out ping is the only phone-home, ever.)

## The observation register (opt-in)

The journal holds your **agent's** thinking — and, if you turn it on, what your agent noticed about *you*. Set `MIRROR=1` in `~/.nightshift/config` and the session reminder invites the agent to log observations about its human collaborator — patterns, blind spots, calls worth revisiting:

```
nightshift observe mysession "he asks for estimates but decides before hearing them —
  the estimate is a comfort ritual, not an input"
nightshift mirror              # your private review inbox
nightshift mirror keep <id>    # -> ~/.nightshift/mirror.md
nightshift mirror drop <id>
```

Observations never appear on the shared page, are excluded from the journal's git repo by default, and nothing downstream consumes them until you `keep` them. **It records; it never acts.** Off by default.

## The Mirror (get better at your own judgment)

Your agent has effectively watched you work for hundreds of hours — it just never told you what it saw. Two instruments:

**The deep read.** `nightshift mirror deep` prints [the Mirror Protocol](share/mirror-protocol.md) — a staged process your agent runs *locally*: mine your own session archives, distill evidence with dated receipts, test its hypotheses against you in interview, then tell you who you are when you work — where your hours die, where they multiply. Everything stays on your machine; that's a hard constraint in the protocol itself.

**The calibration ledger.** Judgment only improves if you score it:

```
nightshift call mysession "this refactor ships by Friday" 80 2026-07-17
nightshift score m1783... right     # when reality reports back
```

Open calls and your hit-rate-vs-confidence show on the rendered page. Uncomfortable, by design.

## Why

Execution is cheap now; the scarce thing is judgment, and the record of it. It's your agent's thinking — and it only survives if it survives execution pressure, which it never does by willpower. So NightShift makes the cheapest action that satisfies the system *be* the thing you actually want: a logged thought. Externalized discipline for the part of the loop nobody can be trusted to do on their own.

MIT. Bring your own agent.

---

Brought to you by the people building [**Konstant**](https://konstant.cloud) — a judgment-under-incompleteness network for commerce between companies' agents. Same conviction, larger scale: execution is cheap now, judgment is the scarce thing, so we build the instruments that protect it. nightshift is one of them.
