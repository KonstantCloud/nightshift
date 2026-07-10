# The Mirror Protocol

*A staged deep-read where your agent mines your own session archives — locally — and tells you who you are, with receipts. Then wires the loop that keeps it true.*

You've been working next to AI agents for hundreds of hours. Every session left a transcript. Your agent has effectively already watched you work longer than any colleague ever has — it just never told you what it saw. This protocol makes it tell you.

**How to run it:** open your agent (Claude Code, Codex) in a fresh session and say: *"Read `<nightshift>/share/mirror-protocol.md` and run it on me."* Budget a real session for it — this is archaeology, not a chat.

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

- **Rhythms:** when do they actually work? Estimate active hours via inter-prompt gaps (cap gaps at ~30 min). Night vs day. Streaks and dead zones — then ask what the dead zones were.
- **Throughput shifts:** machine-actions per active hour over time. Did some practice change (new tooling, new prompting style) visibly multiply leverage? Did rework rise with it?
- **Repeated patterns:** questions they ask again and again, projects rebuilt more than once, threads started and abandoned. Count them.
- **Vocabulary shifts:** terms that appear/disappear across months — they mark changes in how the person thinks, often before the person notices.
- **Where hours die:** the tasks that eat sessions without shipping. Where hours multiply: the moves that consistently pay.

## Phase 3 — Interview

Present hypotheses **one at a time**, framed to be falsified: "The evidence suggests X — but I could be misreading; what was actually happening?" Update the evidence file with their corrections. Do not batch questions; do not lead the witness. 5–8 hypotheses is plenty.

## Phase 4 — The read

Write the deep read: who this person is when they work — evidence first, verdict second. Include the uncomfortable parts (what they avoid, where their ego bites, the gap between what they say matters and where hours go). Include the flattering parts only when the receipts force them. End with: where your hours die, where they multiply, and the one change with the highest expected value.

## Phase 5 — Artifacts

Leave behind, locally:
- **`mirror.md`** — the read, with its receipts.
- **`roadmap.md`** — a 30-day plan derived from it (what to cut, what to double, one experiment).

## Phase 6 — The loop (this is where nightshift comes in)

A mirror that never updates becomes a portrait. Wire the maintenance loop:

- **Observations:** set `MIRROR=1` in `~/.nightshift/config`. The agent logs what it notices about you (`nightshift observe`) to a private inbox; you review with `nightshift mirror`, keep the true ones into `mirror.md`.
- **Calibration:** when you make a falsifiable prediction, log it — `nightshift call <session> "<claim>" <confidence%> [due-date]` — and score it when reality reports back: `nightshift score <id> right|wrong`. The rendered page shows your hit rate against your confidence. This is the only known exercise that actually improves judgment.
- **Cadence:** weekly-ish — review the observation inbox, score due calls, reread the last page of `mirror.md`. Twenty minutes.

---

*The premise, in one line: execution is cheap now; judgment is the scarce thing — and the record of your own judgment is the training data for improving it.*
