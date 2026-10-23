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

**Selection score — a candidate chapter earns a slot only if it passes
all three:**
1. **Signal** — it's visibly hot today: a fresh chapter in the
   last-24h update lists, a live Reddit discussion/release thread, or a
   series in the evergreen US pool (search demand already proven).
2. **The Moment** — the chapter contains ONE scene that fits the locked
   style: a humiliation→power contrast, a refusal, a reveal, a betrayal,
   an absurd premise. Found by skimming the chapter's panels + OCR —
   the short is a moment, never a full-chapter recap.
3. **A hook line** — that moment compresses into one absurd sentence
   for the title/first line. If you can't write the hook, the moment
   isn't strong enough. Skip it.

Mix per day: ~4 trend/new-chapter, ~4 evergreen + Solo inventory.
Never repeat an angle already posted; check the posted log
(goal workspace `posted_log.md`) first. Write the batch list (series,
chapter, angle, hook line) before building.

**The context ladder — NEVER read a whole series to use one chapter.**
A new chapter of a 222-chapter series needs only enough context to
write ~11 honest sentences. Climb only as high as needed:
1. **The chapter itself** — panels + OCR give the moment, the players
   present, and what literally happens. Usually sufficient.
2. **The chapter's own framing** — many chapters open with a synopsis
   or "previously" panels; the series page blurb gives premise + MC.
3. **Community context** — the Reddit chapter thread and/or the series'
   fandom wiki page: who the MC is, the power system, the current arc.
   Two minutes, written by fans, exactly the context a viewer has.
4. **The previous 1–2 chapters** — skim panels/OCR only if a callback
   in this chapter makes no sense without them.
Hard stop: never ingest more than ~3 chapters of backstory for one
short, and never state a "fact" in a script that the ladder didn't
actually verify. Roles-not-names style keeps the exposure low anyway:
the script needs the *situation* right, not the lore.

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

## Voice (locked)
Deepgram **aura-2-orion-en** at **native 1.3x** — Deepgram's flagship
male Aura-2 voice, and the voice of Short #1 (the one already
performing). One consistent voice is part of the channel's identity;
never switch voices per video. Timings always derive from the final
1.3x audio.

## BGM policy (CHANGED — user directive 2026-10-24)
- **NO BGM in the daily run's shorts.** Render every short with
  `render --no-bgm` (voice-only mix: no music bed, no sting/riser
  layers). The owner adds music themselves after delivery — do not
  add, synthesize, or source any music track for the daily run.
- **Never rip audio out of another channel's video** (standing rule,
  unchanged): copyright claims + YouTube's *reused content* policy
  can reject the channel from the Partner Program.
- Competitor research during the daily step is now angles/hooks only
  (no BGM track identification); the old library research stays at
  `~/workspace/research_notes/mangvoro-competitor-bgm/report.md` as
  history.

## Script length (user directive 2026-10-24)
The Day-1 shorts were too wordy. Scripts are LEAN now: ~110–170 words
total, sentences ≤22 words, target 28–60s of VO. Cut every sentence
that doesn't escalate. The script validator enforces this — a script
that fails the band is rewritten shorter, never padded out.

## Monetization levers (how the 30 days are actually attacked)
No honest plan *guarantees* 10M views in 30 days — anyone who does is
lying. What we control, we max out:
1. **Volume + consistency** — 6–8/day, never a missed day; the
   algorithm rewards streaks and each short is a lottery ticket.
2. **Trend-riding** — today's chapters of hot series (selection §2),
   so we borrow existing search/demand instead of creating it.
3. **Retention engineering** — hook in 2s, a visual cut every 1–2s,
   cliffhanger freeze + end question; Short #1's 59.4% APV is the
   floor to beat, reviewed per short in analytics.
4. **Double down on winners** — any short that breaks out gets a
   sequel/part-2 within 24–48h while its topic is warm; sequels of
   hits are the cheapest views on the platform.
5. **US timing** — the 5-day test finds the windows; then volume
   concentrates there.
6. **Engagement** — pinned end-question on every short; reply to early
   comments (they seed the comment section viewers read).
7. **Series packaging** — shorts from one series carry a series
   playlist; a viewer who lands for one episode finds the rest.
8. **YPP-safety** — transformative narration + own voiceover + legal
   BGM only; no reused audio, no fake engagement, ever. A policy
   rejection at day 30 wastes the whole sprint.

## Standing rules
- Shorts style = the locked reference style (see AGENT_WORKFLOW). No
  long-form editing style, ever, on this channel's shorts.
- Only each series' own chapter panels; no outside art; no grey-mask
  panels; fresh filename per render.
- Titles/captions in clear international English (US audience): no
  regional slang.
- Never delete or alter the user's pre-existing videos (the 6 unlisted
  long-forms, the duplicate short) without an explicit instruction.
