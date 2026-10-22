# Shorts Workflow — v1 (2026-10-22)

For YouTube Shorts / TikTok. This workflow is separate from the long-form chapter
software — do NOT use the software's editing style for shorts. Reusable for any series.

## The style (reverse-engineered from the reference short)

1. **Dynamic visual pacing** — frequent rapid cuts between panels (every 1–2s);
   panels zoomed or panned to emphasize reactions and crucial moments.
2. **Text-overlay storytelling** — large, bold, ALL-CAPS captions placed centrally
   over the artwork; the story must be followable with the sound off.
3. **Integrated UI elements** — graphic overlays that visualize the premise
   (here: constellation/system-notification look, end-question card).
4. **Visual hierarchy** — hook words highlighted with color contrast (yellow/red)
   so the point lands instantly.
5. **Rhythmic transitions** — every cut synchronized to the voice-over narration.

## Hard rules

- 9:16, 1080×1920, 30fps. Target length 45–100s.
- **VO pace is 1.3x** — and ALL timings (cuts, captions) are measured on the final
  1.3x audio, never before the speed is applied.
- Only the series' own panels, from the chapters the script covers. No outside art.
- No grey-mask panels: never use a shouting face + dominant speech bubble panel;
  drop it or crop the face with the bubble excluded.
- Measure every crop on the single panel image, never on a composite sheet.
- Whisper/alignment always with the venv python (system python falls back to
  estimated timing — forbidden here too).
- Fresh filename for every render, never reuse one.

## Stage 0 — Script lock

Script approved (see SHORTS_SCRIPTS.md). Split it into spoken sentences.
`[music]` markers are edit cues, never spoken. Note the hook caption (first 2s)
and the end-card question before any production starts.

## Stage 1 — Voice-over (1.3x)

- Synthesize per sentence via Deepgram (key-file route, same as chapter TTS)
  at native speed 1.3. Fallback if a voice rejects 1.3: synthesize at 1.0 and
  apply pitch-preserved `atempo=1.3`. Use ONE method per short and record which.
- Join sentences with ~120ms gaps; loudness-normalize.
- Measure the total: 45–100s. Too long → trim script beats; never push past 1.3x.
- **Gate:** whisper the final VO and diff against the script — no dropped or
  garbled sentences.

## Stage 2 — Beat sheet (timing map)

Whisper-align the FINAL 1.3x VO → word timestamps. Build the beat sheet
(`shorts/shortN/beats.md`): one row per clause — text, start, end.
Every cut and caption is placed from this sheet. No by-ear timing.

## Stage 3 — Panel picks + EDL

- One panel per beat (two for beats over ~2.5s): reaction face for emotional
  beats, action panel for reveals, widest panel for scene-setting.
- Write the EDL (`shorts/shortN/edl.md`): beat → panel id → crop box (fractions
  of the single panel) → motion (push-in on reveals, slow pan on scenes,
  static + shake on impacts) → caption chunk.
- **Gate (review before render):** every panel depicts its beat's subject;
  faces whole inside the 9:16 crop; no mask-risk panels; the LAST panel is the
  strongest cliffhanger frame.

## Stage 4 — Render (manual ffmpeg, not the chapter software)

- Build each shot from its panel crop at 1080×1920 with the EDL motion;
  cuts exactly on beat boundaries from the beat sheet.
- Music bed under the VO, ducked; riser/swell at each `[music]` marker;
  sting under the opening hook. Mix and loudness-normalize.

## Stage 5 — Captions + end card

- ALL-CAPS bold captions, centered, phrase chunks timed from the beat sheet;
  hook words in yellow/red; thick stroke + shadow for legibility.
- The hook caption is on screen within the first 2 seconds, over a strong panel.
- Final 2–3s: freeze on the cliffhanger panel + series name + the end question
  in big caps + "Full story on the channel".

## Stage 6 — QC gates (all must pass before delivery)

1. **Sync:** 5 random cuts checked against the beat sheet — each within ~0.1s.
2. **Mute test:** captions alone tell the whole story.
3. **Hook test:** first 2s = hook caption + strong face/action panel.
4. **Frame check:** first frame of every cut — no cut faces, no sliced text,
   no grey masks, no watermarks.
5. **Audio:** VO clear over the music everywhere; no clipping.
6. **File:** 1080×1920, duration = VO + end card, fresh filename.

## Stage 7 — Deliver + posting pack

Deliver the mp4 plus: title (hook + series name), description carrying the end
question, hashtags, and the end question as the pinned comment.

## Folder layout

`shorts/shortN/` → `script.md`, `vo/` (per-sentence + final VO), `beats.md`,
`edl.md`, `out/` (final renders).
