# 🌒 nightshift

**Your agent remembers what it shipped. It forgets what it thought. nightshift keeps the thinking — because the harness makes it.**

Agentic coding grows code faster than understanding. nightshift grows the understanding: an encrypted, multi-session work journal your agents are *forced* to think into, plus a mirror that points the same instrument back at you.

```bash
curl -fsSL https://night-shift.sh/install | bash
```

Four instruments, one thin core:

| | |
|-|-|
| **The journal** | Append-only, multi-session, published as one AES-encrypted page you host anywhere |
| **The enforcement** | A `Stop` hook that won't let a turn end on a receipt — a real thought, or the turn doesn't close |
| **nowish** | Sessions leave notes for each other, so five parallel agents don't collide |
| **The mirror** | What your agent noticed about *you*, your predictions scored, and a deep read of who you are when you work |

Works in **Claude Code** and **Codex** — same hook scripts, two registration files. MIT.

## The journal + the enforcement

The interesting record isn't the git log — it's what the agent *noticed*: the connection it made at 2am, the doubt it didn't say, the thing it got wrong and why. That evaporates every session, because agents (like people) drift to logging receipts under execution pressure. So the discipline lives in the harness:

```
nightshift log diary mysession "the bug wasn't the cache — two sessions share one
  lock file. I only saw it because the timestamps were 4h apart. worth a helper."
nightshift publish
```

When a turn tries to end on `deployed X ✓` and nothing else, the Stop hook blocks it — once — until a real `diary`/`idea` entry exists. Entries are per-session `jsonl`, append-only, no clobbering; the rendered page is encrypted client-side (the host never sees plaintext); the password gate is password-manager-native — save it once in your browser and it autofills, or `nightshift pw` copies it from the macOS Keychain. Sentinels are keyed per session, so concurrent agents never block each other.

```
nightshift send relay all "claiming the deploy — hold until it lands"   # nowish
nightshift inbox mysession && nightshift pick <id> mysession
```

## The mirror

Your agent has effectively watched you work for hundreds of hours. Three ways to get that back:

**1. Observations (opt-in).** With `MIRROR=1`, your agent logs what it notices about its human — patterns, blind spots — to a private inbox. Never on the shared page, git-ignored, and nothing downstream consumes it; anything wrong, you drop, and what survives folds into your next deep read. *It records; it never acts.*

```
nightshift observe mysession "decides before hearing the estimate — it's a comfort ritual"
nightshift mirror                    # the register — drop <id> removes what's wrong
```

**2. Calls.** About to commit to something uncertain? Your agent offers it in the moment: *"want to call it?"* When a call comes due, your next session opens by asking how it resolved. The page keeps your hit rate against your confidence — the only known exercise that actually improves judgment.

```
nightshift call mysession "this refactor ships by Friday" 80 2026-07-17
nightshift score m1783... right      # due calls are chased automatically at session start
```

**3. The deep read.** [`MIRROR.md`](MIRROR.md) is a staged protocol your agent runs **locally**: mine your session archives, distill evidence with dated receipts, test its hypotheses against you in interview — then tell you who you are when you work. Where your hours die. Where they multiply. Nothing leaves your machine; that constraint is written into the protocol.

```bash
curl -fsSL https://night-shift.sh/mirror | pbcopy    # paste into a fresh session: "run this on me"
```

## Install

The one-liner above runs a three-question interview (Enter accepts every default; silent in CI), drops `nightshift` on your PATH, `git init`s your journal so your thinking is versioned from entry one, and offers to wire your agent's hooks itself. Nothing runs as root — [read it first](https://night-shift.sh/install).

Wire-in, if you skipped the offer:

- **Claude Code:** `bash adapters/claude-code/install.sh` — merges into `~/.claude/settings.json`; hooks load automatically next session.
- **Codex:** append `adapters/codex/hooks.toml` to `~/.codex/config.toml` — Codex's native hooks take the same stdin JSON, so the identical scripts run. See [`adapters/codex/README.md`](adapters/codex/README.md).

Manual install, upgrades, health:

```bash
git clone https://github.com/KonstantCloud/nightshift && export PATH="$PWD/nightshift/bin:$PATH"
pip install cryptography      # optional — enables the encrypted page
nightshift upgrade            # zero-copy git pull; `doctor` says when you're behind
```

> The installer sends one anonymous ping so we can count adoption — a tally, no machine ID, no personal data. Opt out with `NIGHTSHIFT_NO_TELEMETRY=1`. That's the only phone-home in the whole system.

## How it's built (and how thin)

```
bin/nightshift    the CLI — init · log · send/inbox/pick · observe/mirror · call/score/due
                  render · publish · doctor · upgrade
lib/              render.py (entries -> encrypted page) · inbox.py
hooks/            SessionStart / Stop / PostToolUse — harness-agnostic, stdin JSON
adapters/         per-harness registration (claude-code, codex)
MIRROR.md         the deep-read protocol         share/reminder.txt   the injected practices
```

Measured, not vibed: **~540 lines total. ~250 tokens of context injected once per session — the entire ongoing footprint.** The Stop block is ~46 tokens, fires at most once per working turn. No server, no accounts, no database. Keep `share/reminder.txt` lean — it's the part that costs context.

**Where everything lives** — one home (`NIGHTSHIFT_HOME`, default `~/.nightshift`), one private git repo. Every session of every agent on the machine — Claude Code and Codex alike — writes here, each to its own append-only file, so parallel agents converge on one page without ever clobbering each other:

```
~/.nightshift/
  entries/<date>-<session>.jsonl   the journal — one file per session per day     versioned
  nowish.jsonl                     inter-session messages                          versioned
  mirror/read.md · roadmap.md      the deep read + your 30-day plan               versioned
  observations.jsonl               the UN-reviewed inbox                           ignored
  .password · index.html · .pending*      secret · derivable render · machine state     ignored
```

The rule that decides every row: **version what you've reviewed; never version what you haven't.** `nightshift publish` auto-commits the home, which makes the best property real: `git -C ~/.nightshift log -p mirror/read.md` shows how the read of you changed over months. Your identity, diffable.

## Why

Execution is cheap now; the scarce thing is judgment, and the record of it. Thinking never survives execution pressure on willpower — so nightshift makes the cheapest action that satisfies the system *be* the thing you actually want: a logged thought, a priced prediction, an observation you can check.

## Credits

- **The Mirror Protocol** grew from a self-analysis prompt that circulated on X in mid-2026. We don't know the original author — [tell us](https://github.com/KonstantCloud/nightshift/issues) and we'll credit them prominently.
- Brought to you by the people building [**Konstant**](https://konstant.cloud) — a judgment-under-incompleteness network for commerce between companies' agents. Same conviction, larger scale: execution is cheap, judgment is scarce, so we build the instruments that protect it.

MIT. Bring your own agent.
