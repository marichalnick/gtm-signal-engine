# Signal-to-Outreach Engine

**Find the right account at the right moment, verify the signal, pick the right person, and write one relevant question. Then measure what actually worked.**

A reproducible demo of the signal-based prospecting workflow I run as a business developer in enterprise AI security. All companies, people, signals and results here are **fictional**: the demo sells a made-up AI-governance offer to made-up European enterprises.

```bash
python run.py                     # no dependencies, no API key
python run.py --today 2026-11-15  # watch signals decay and tiers shift
```

## Why this exists

Most outbound fails for one of three reasons:

1. **Wrong timing:** a good account, contacted when nothing is changing.
2. **Wrong person:** the highest title instead of the person who owns the problem.
3. **No learning:** nobody tracks which trigger, angle or call to action created the meeting.

This engine addresses all three, and keeps a human in charge of every message.

## The pipeline

```
 SIGNAL SOURCES                         VERIFY & SCORE              ACT                       LEARN
 ┌───────────────────────┐
 │ Google News alerts    │──┐
 │ Job postings          │──┤        ┌──────────────────┐      ┌──────────────────┐     ┌──────────────────┐
 │ EU AI Act registry    │──┼──────▶ │ confidence       │ ───▶ │ pick stakeholder │ ──▶ │ log every touch  │
 │ LinkedIn keywords     │──┤        │ decay over time  │      │ no repeats       │     │ reply & meeting  │
 │ Manual input (URL)    │──┘        │ ICP fit × signal │      │ draft 1 question │     │ rate per trigger │
 └───────────────────────┘           │ → Tier 1/2/...   │      │ human approves   │     │ angle, CTA       │
                                     └──────────────────┘      └──────────────────┘     └──────────────────┘
```

| # | Step | What it does | File |
|---|---|---|---|
| 1 | **ICP & accounts** | Sector, size, AI maturity, regulation. Disqualify what doesn't fit. | `data/accounts.csv` |
| 2 | **Collect signals** | Five pluggable sources, one adapter each. | `engine/sources.py` |
| 3 | **Verify** | Primary source = usable. Hearsay goes to a human first. | `engine/scoring.py` |
| 4 | **Score & tier** | `ICP fit × signal strength × decay × confidence` → Tier 1, Tier 2, Nurture, Verify first, Disqualified. | `engine/scoring.py` |
| 5 | **Buying committee** | Each trigger maps to the role that owns it. Cooldowns prevent hitting the same person or angle twice. | `engine/committee.py` |
| 6 | **Draft** | Signal → pain hypothesis → one question. No product pitch. | `engine/messaging.py` |
| 7 | **Human review** | Nothing is sent automatically. Approve, edit or reject. | `output/drafts.md` |
| 8 | **Attribution** | Reply and meeting rate per trigger, angle and call to action. | `engine/report.py` |

## Example output

**Shortlist** (`output/shortlist.md`)

| Tier | Account | Fit | Score | Reason |
|---|---|---:|---:|---|
| Tier 1 | Nordbank | 1.0 | 77 | ai_rollout (5d old) |
| Tier 1 | Vega Pharma | 0.96 | 74 | keyword_post (3d old) |
| Tier 1 | Helios Insurance | 0.93 | 54 | hiring_ai_governance (10d old) |
| Verify first | Kestrel Retail | 0.53 | 0 | only unverified signals |
| Nurture | Atlas Asset Management | 0.96 | 4 | ai_act_registration (96d old) |
| Disqualified | Tiny Studio | 0.13 | 9 | below minimum company size |

Note Atlas: a perfect-fit account with a strong signal, but the signal is three months old. **Timing matters as much as fit.**

**Draft** (`output/drafts.md`)

```
Hi Lukas,

I saw your post about agent visibility.

Quick question: you wrote that knowing what your agents actually do is the
biggest gap. Is that a tooling gap or an ownership gap today?

If useful, here's a 20-minute slot this week: [calendar link]
```

Each draft shows the trigger, the source, its age, why this person was chosen and the pain hypothesis behind the question, so the reviewer can judge it in seconds.

**Discipline built in:** Nordbank is the top account, but it is **skipped** because the same angle was used there 20 days ago. A new message needs a new angle or a different stakeholder.

**Attribution** (`output/attribution_report.md`, synthetic history)

| Call to action | Sent | Reply rate | Meeting rate |
|---|---:|---:|---:|
| calendar_link | 5 | 100% | 80% |
| ask_for_call | 5 | 20% | 0% |

## Design choices

- **Verification before volume.** An unverified trigger in an email to a CISO costs more credibility than it gains. Secondary sources are never used directly.
- **Signals decay.** Half-life of 21 days: a funding round from yesterday is gold, from six months ago it is noise.
- **One question, not a pitch.** The goal of a first message is a conversation, not a demo.
- **Low-friction call to action.** A concrete slot beats "can I have your number?".
- **Human in the loop.** AI drafts, a person decides.
- **Every touch is logged.** Without attribution, outbound stays anecdotal.

## Lessons behind it

This repo is a clean reimplementation of what I learned in real outbound work:

- **I used to lack attribution.** I couldn't say which trigger or message created a meeting. Step 8 exists because of that.
- **Replies did not turn into meetings** when I asked prospects for extra effort. The calendar-link CTA is the fix.
- **I tended to build tooling before proving the bottleneck.** This version is deliberately small: no framework, no dependencies, just the logic.

## How I run this in practice

| Step | Tools I use |
|---|---|
| Accounts & contacts | Apollo, LeadIQ, Clay |
| Signal monitoring | Claude scheduled tasks |
| Research & buying committee | Claude, LinkedIn (manual) |
| Tracking & dossiers | Notion, Excel |

The demo replaces each of these with a local file, so anyone can run it.

## Data & compliance

- All data is synthetic. URLs point to `example.com`.
- Source adapters are written for **permitted** inputs: RSS feeds, public registries, job-board feeds, compliant exports and manual input. This repo contains no scraping code.
- Real outreach to EU contacts must respect GDPR (legitimate interest, opt-out, data minimisation).

## Limitations

- Weights and thresholds are hand-set, not learned from data.
- Ten synthetic historical touches are a demonstration, not evidence.
- Drafts are template-based. An LLM can replace `messaging.py`, but a human should still approve every message.
- No scheduler: in practice this runs daily (Claude scheduled tasks, cron or n8n).

## Next steps

- [ ] Learn scoring weights from logged outcomes.
- [ ] LLM drafting with the same inputs and a verification check on every factual claim.
- [ ] Opportunity and pipeline stages after the meeting, not only replies and meetings.
- [ ] Simple dashboard on top of the attribution log.
