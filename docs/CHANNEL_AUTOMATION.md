# Mangvoro — Daily Shorts Automation

The operating plan for the YouTube Shorts channel **Mangvoro (@Mangvoro)**.
Runs with `docs/AGENT_WORKFLOW.md` (how to build a short) — this file says
WHAT to build each day, WHEN to post it, and HOW to report.

## Mission

- Target: **US viewers**, English titles/captions.
- Goal: YouTube Partner Program — stretch target 30 days
  (1,000 subs + 10M Shorts views/90d; first tier at 500 subs + 3M views).
- Baseline (2026-10-23): 0 subscribers. Short #1 "The world's strongest
  man is broke" (Solo Swordmaster ch1): 1,149 views, 29 likes, 1 comment,
  **59.4% average percentage viewed** in its first ~11 hours.

## The daily run (starts 04:00 IST)

### 1. Research — what's hot TODAY (30–45 min)
- r/manhwa (hot + today's chapter-release/discussion threads): which
  series are people talking about right now.
- Scan-site latest updates (AsuraScans home / latest-updates list):
  which series just dropped a chapter in the last 24h.
- Evergreen US-popular pool (proven search demand): Solo Leveling,
  The Beginning After the End, Nano Machine, Eleceed, Tower of God,
  Omniscient Reader, Mercenary Enrollment, SSS-Class Revival Hunter,
  Pick Me Up Infinite Gacha, The Extra's Academy Survival Guide,
  Revenge of the Baskerville Bloodhound, The Infinite Mage.
- Our own inventory: Solo Swordmaster ch1–23 (fully understood, fastest
  to produce) — always eligible filler so the daily count never fails.

### 2. Select — 8 shorts (the daily batch)
For each candidate chapter ask: *does it contain ONE moment that fits the
locked short style* (a humiliation→power contrast, a reveal, a refusal, a
betrayal, an absurd premise)? If yes, it's in. Mix per day:
- ~4 from today's hot/new chapters (trend-riding),
- ~4 from evergreen pool + Solo Swordmaster inventory (reliability).
Never repeat an angle already posted; check the channel's posted log
(goal workspace `posted_log.md`) first. Queue the batch as a written
list (series, chapter, angle, hook line) before building.

### 3. Build — Shorts Builder pipeline
Per `docs/AGENT_WORKFLOW.md`: ingest → understand → script → VO → beats
→ EDL → render → QC frame sheet check. Parallelize with subagents
(one per short) where possible. A short that fails QC twice is dropped
from the batch and replaced from the Solo inventory — the count matters,
but a defective short never ships.

### 4. Titles (US search + click style)
Format: `<Hook statement> | <Series Name>` or the hook as a question.
Rules: the hook IS the title (curiosity gap, no spoiler of the payoff),
series name always present (search), ≤70 characters where possible,
no clickbait the video doesn't pay off. Description: the end question +
one line + hashtags (#manhwa #manhwarecap #shorts + series tag).
Pinned comment: the end question, posted right after publish time.

### 5. Upload + schedule
Upload each finished short via YouTube Studio (browser, already signed
in as Mangvoro) as **Unlisted**, then set **Schedule** to its slot.
**Test grid (Days 1–5) — 8 slots/day, 3 hours apart (IST):**
06:00, 09:00, 12:00, 15:00, 18:00, 21:00, 00:00, 03:00
(= 20:30, 23:30, 02:30, 05:30, 08:30, 11:30, 14:30, 17:30 US Eastern —
deliberately sampling US morning, lunch, and evening-prime windows).
Rotate the whole grid +1 hour each test day to widen the sample.
After each slot time passes, add the pinned comment to the now-public
short (do it in the next day's run for the previous day's late slots).
**If the Studio session is signed out: produce everything, hold the
uploads, and report — never fight a login or a CAPTCHA.**

### 6. Report (end of every run, to the user)
- Today's batch: 8 titles + series/chapter + scheduled time (IST + ET).
- Yesterday's results (from Studio analytics): views, likes, subs gained,
  average percentage viewed per short; channel totals vs YPP targets.
- Any short that failed/dropped and why.

## The 5-day timing test (Days 1–5 → 40 shorts)
Purpose: learn WHEN US viewers actually watch us. After Day 5, analyze:
views + average percentage viewed grouped by publish slot (ET) and by
series/angle. Then lock the ongoing schedule to the best 3–4 windows and
keep volume at 6–8/day inside them. Record findings in the goal
workspace (`timing_test.md`) — that analysis, not habit, sets the
long-term posting times.

## Standing rules
- Shorts style = the locked reference style (see AGENT_WORKFLOW). No
  long-form editing style, ever, on this channel's shorts.
- Only each series' own chapter panels; no outside art; no grey-mask
  panels; fresh filename per render.
- Titles/captions in clear international English (US audience): no
  regional slang.
- Never delete or alter the user's pre-existing videos (the 6 unlisted
  long-forms, the duplicate short) without an explicit instruction.
