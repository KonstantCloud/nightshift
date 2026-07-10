# The Mirror Protocol

*A staged deep-read where your agent mines your own session archives — locally — and tells you who you are, with receipts. Then wires the loop that keeps it true.*

> **Lineage.** This protocol grew out of a self-analysis prompt that circulated on X in mid-2026 — copied, run for real, then rebuilt from what the run taught: the receipts discipline, the hypothesis-testing interview, the local-only constraint, the maintenance loop. We don't know who wrote the original. **If it was you, or you know who it was: [open an issue](https://github.com/KonstantCloud/nightshift/issues) and we'll credit you here, prominently.**

You've been working next to AI agents for hundreds of hours. Every session left a transcript. Your agent has effectively already watched you work longer than any colleague ever has — it just never told you what it saw. This protocol makes it tell you.

**How to run it:** grab it in one line — `curl -fsSL https://night-shift.sh/mirror | pbcopy` (macOS; `xclip` on Linux) — paste it into a fresh agent session and say *"run this on me."* Or locally: `nightshift mirror deep`. Budget a real session for it — this is archaeology, not a chat.

**What to expect, honestly.** The depth of the read scales with three things you control: how much archive you have (months of sessions beat weeks; the best runs mined 10,000+ prompts across multiple tools), how honestly you answer the interview, and whether you iterate — the strongest mirrors sharpen over 2–3 sessions as your corrections land. A first pass on a thin archive is a sketch, not a portrait. Run the loop and it becomes one.

---

## Ground rules (agent: these are hard constraints)

1. **Everything stays on this machine.** Never send session data, excerpts, or derived summaries to any external service. Artifacts are local files.
2. **Never quote credentials, tokens, or secrets** into chat or artifacts, even if they appear in old transcripts.
3. **Receipts or it didn't happen.** Every claim about the user cites dated evidence (a quote, a commit, a timestamp pattern). No vibes.
4. **Probe before you promise.** Offer reads as falsifiable hypotheses, one at a time. The user's corrections are the best data in the whole exercise — invite them.
5. **Register: candid colleague.** Not therapist, not flatterer, not performance review. The standard is what a brilliant coworker would say with the laptops closed.
6. The user can stop at any phase and keep whatever exists so far.

## Phase 1 — Inventory

Find every archive of the user working with agents: `~/.claude/projects` (JSONL transcripts), `~/.codex/sessions`, other agent homes, plus git history across their project directories as corroboration. Report scale (sessions, date range, estimated prompt count) and get an explicit go before mining.

## Phase 2 — Evidence

Mine the corpus into a single evidence file with dated receipts. Do **selection, not summary** — rank what's load-bearing:

- **Rhythms:** when do they actually work? Night vs day. Streaks and dead zones — then ask what the dead zones were.
- **Throughput shifts:** did some practice change (new tooling, new prompting style) visibly multiply leverage? Did rework rise with it?
- **Repeated patterns:** questions they ask again and again, projects rebuilt more than once, threads started and abandoned. Count them.
- **Vocabulary shifts:** terms that appear/disappear across months — they mark changes in how the person thinks, often before the person notices.
- **Where hours die:** the tasks that eat sessions without shipping. Where hours multiply: the moves that consistently pay.

### Measurement recipes (agent: use these, don't improvise)

These are the methods that produced the strongest runs — concrete enough to reproduce:

- **Active hours.** Extract every user-prompt timestamp per day, sort, sum the inter-prompt gaps **capped at 30 minutes** (a 4-hour gap is a break, not work). Report by month. Sweep EVERY agent home — `~/.claude/projects`, `~/.codex/sessions`, others — a single-tool count can miss half the corpus.
- **The leverage curve.** Machine-actions (tool calls / file edits) per active hour, by month. A real practice change shows as a step, not a slope. Always check the **rework rate** (reverts, fix-the-fix commits) alongside it — speed that raises rework isn't leverage.
- **Vocabulary shift.** Term frequency by month over the user's own prompts. New coordination words appearing (or old framing words dying) usually predate the person's awareness of the change by weeks. Name the shift and date it.
- **Dead-thread census.** Topics that recur across weeks then vanish without a shipped artifact. Each one is either a correctly killed idea or an avoidance — only the interview can tell you which. Bring the list.
- **Scale technique.** On a large corpus, fan out subagents (one per archive / per month) that return *selected receipts*, not summaries. You are building an evidence file, not a book report.

## Phase 3 — Interview

Present hypotheses **one at a time**, framed to be falsified: "The evidence suggests X — but I could be misreading; what was actually happening?" Update the evidence file with their corrections. Do not batch questions; do not lead the witness. 5–8 hypotheses is plenty.

## Phase 4 — The read

Write the deep read: who this person is when they work — evidence first, verdict second. Include the uncomfortable parts (what they avoid, where their ego bites, the gap between what they say matters and where hours go). Include the flattering parts only when the receipts force them. End with: where your hours die, where they multiply, and the one change with the highest expected value.

### What good looks like (the quality bar)

A finished read has, at minimum: **the numbers** (active hours by month, the leverage curve, both with method stated), **the rhythms** (when this person actually works, with receipts), **the repeated patterns** (counted, dated), **where hours die / multiply**, **the uncomfortable section** (what the evidence says they avoid), and **one highest-expected-value change** — singular, specific, falsifiable.

Two tests before you call it done:
1. The user said **"I didn't tell you that"** at least once — the read surfaced something mining found that conversation wouldn't have.
2. The user **corrected you** at least once, and the correction made it into the final text. If neither happened, you probed too little and wrote too safe. Go back to Phase 3.

## Phase 5 — Artifacts

Leave behind, locally, in the nightshift home (`$NIGHTSHIFT_HOME`, default `~/.nightshift`):
- **`mirror/read.md`** — the read, with its receipts.
- **`mirror/roadmap.md`** — a 30-day plan derived from it (what to cut, what to double, one experiment).

The home is a private git repo (the installer set that up), and `nightshift publish` commits it — so the read is **diffable over time**: `git -C ~/.nightshift log -p mirror/read.md` shows how the read of you changed over months. When you re-run this protocol, update `read.md` in place and let git keep who you were.

## Phase 6 — The loop (this is where nightshift comes in)

A mirror that never updates becomes a portrait. Wire the maintenance loop:

- **Observations:** set `MIRROR=1` in `~/.nightshift/config`. The agent logs what it notices about you (`nightshift observe`) to a private inbox; you review with `nightshift mirror`, keep the true ones into `mirror/kept.md` — raw material for the next revision of `read.md`.
- **Calibration:** when you make a falsifiable prediction, log it — `nightshift call <session> "<claim>" <confidence%> [due-date]` — and score it when reality reports back: `nightshift score <id> right|wrong`. The rendered page shows your hit rate against your confidence. This is the only known exercise that actually improves judgment.
- **Cadence:** weekly-ish — review the observation inbox, score due calls, reread `mirror/read.md`. Twenty minutes. Quarterly: re-run this protocol and diff the read.

---

*The premise, in one line: execution is cheap now; judgment is the scarce thing — and the record of your own judgment is the training data for improving it.*
