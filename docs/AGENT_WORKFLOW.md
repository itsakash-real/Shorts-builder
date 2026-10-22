# Shorts Builder — Agent Workflow

**Give this whole file to the agent.** It is everything a fresh agent needs to
run the Shorts Builder product end to end. The user will give you manhwa
chapter link(s) and ask for 1, 2, 3 or more shorts. You drive the two creative
stages (script, panel picks); the software does everything else.

Repo: `itsakash-real/Shorts-builder` — clone it and work inside it.

---

## 0. Setup (once)

```bash
git clone https://github.com/itsakash-real/Shorts-builder.git
cd Shorts-builder
python3 -m venv .venv && .venv/bin/pip install pillow numpy requests rapidocr-onnxruntime
```

Requirements on the machine:

- `ffmpeg` and `ffprobe` on PATH.
- A Deepgram API key: env `DEEPGRAM_API_KEY`, or a key file at
  `~/.config/manhwa/deepgram.key` (the software reads it; never print it,
  never commit it).
- A python with `pywhispercpp` + the `small.en` model for the beat-alignment
  step. Point the env var `WHISPER_PYTHON` at it if it is not the default
  (`~/workspace/venvs/manhwa-ocr/bin/python`). If no whisper python exists,
  install `pywhispercpp` into a venv and set `WHISPER_PYTHON` to it.

All commands below are run as `.venv/bin/python -m shorts_builder.cli ...`
from the repo root.

## 1. The job, in one paragraph

Input: chapter link(s) + a count of shorts. Output per short: one finished
1080×1920 mp4 (~45–100s) + a posting pack. The quality bar is the golden
reference in `examples/short1-golden/` (beat sheet + edit list of a proven
short) and the worked example in `projects/test-solo/` (script, EDL, beats,
posting pack from a real run). Match that standard: a cut every 1–2s locked
to the voice-over, big Anton ALL-CAPS captions with hook words in yellow,
a hook in the first 2 seconds, a cliffhanger freeze + series name + an
on-screen question at the end.

## 2. Pipeline

Run these stages in order. Do not skip gates.

### Stage 1 — Ingest (software)

```bash
.venv/bin/python -m shorts_builder.cli new <project> --chapters <url1> [url2 ...]
```

Fetches each AsuraScans chapter page, extracts the embedded page images
(entry #1 is a credits banner — the software skips it as a panel source),
slices panels at gutter rows, and writes `projects/<project>/media/chN/
panels.json` + panel PNGs (`P<page>-<idx>`, e.g. `P032-04`). One `--chapters`
entry per chapter, in story order. If it reports 0 pages, the URL is wrong —
get the chapter URL from the series page (`/comics/<series>/chapter/<n>`).

### Stage 2 — Understand (software + you)

```bash
.venv/bin/python -m shorts_builder.cli understand <project> --chapter 1
```

Produces per-panel OCR text (`panels_ocr.json`) and contact sheets
(`media/chN/sheets/`). **Your job:** read the OCR text in panel order to
learn the chapter's story — who, what happens, the biggest contrasts and
the cliffhanger. Also skim the sheets so you know what the art looks like.
Do NOT trust OCR wording for facts it garbles; trust the story shape.

### Stage 3 — Script (YOU write it; software validates)

Write `projects/<project>/shorts/short<N>/script.json`:

```json
{
  "series": "Solo Swordmaster",
  "title": "<hook> | <Series>",
  "hook_caption": "THE HOOK IN CAPS. SECOND SENTENCE.",
  "end_question": "THE COMMENT-BAIT QUESTION IN CAPS?",
  "hashtags": ["#manhwa", "#manhwarecap", "#shorts"],
  "sentences": [
    {"text": "A spoken sentence, written as a comma chain of clauses.",
     "beats": [{"caption": "CAPTION CHUNK IN CAPS", "highlight": ["HOOKWORD"],
                "music": null}]}
  ]
}
```

Rules (full spec: `docs/SCRIPT_STYLE.md` — read it before writing):

- One breathless past-tense chain: beats linked by So / But / That's when /
  Luckily. Hook in the first line — the most absurd version of the premise,
  stated flat. No greeting, no setup.
- One idea per beat, and every beat must be showable in ONE panel.
  ~4–9 spoken words per beat; a sentence is a chain of its beats' clauses.
- Escalation ladder, not a summary. Contrast pairs are the engine
  (strong/broke, robbed him/begged him, any man would beg/he refused).
- Names are rationed: characters enter by role ("a young agent", "the
  officials"). The only name spoken is the series title, in the final
  sentence: "The name is <Series>."
- End on the cliffhanger, never the resolution. The `end_question`
  continues the story in the comments.
- Put `"music": "sting"` on the impact beat, `"music": "shift"` on the
  tone-turn beat. (The end card gets its swell automatically.)
- Each sentence ≤34 words; each caption ≤8 words; total ≈45–100s of
  speech (~3.55 words/sec at 1.3x — aim ~160–320 words); ≥15 beats
  (golden: 25–26).
- If the user asked for multiple shorts, write one script per short, each
  with a DIFFERENT angle/moment from the chapters — never the same story
  retold. Spread them across the chapters' biggest moments.

Validate:

```bash
.venv/bin/python -m shorts_builder.cli script <project> short<N>
```

Fix whatever it flags. Do not proceed on an invalid script.

### Stage 4 — Voice-over (software)

```bash
.venv/bin/python -m shorts_builder.cli vo <project> short<N>
```

Deepgram per-sentence TTS at native speed 1.3 (voice aura-2-orion-en),
~120ms gaps, loudness-normalized → `shorts/short<N>/vo/vo_final.wav`.
Sanity-check the duration it lands in the 45–100s band.

### Stage 5 — Beat sheet (software)

```bash
.venv/bin/python -m shorts_builder.cli beats <project> short<N>
```

Whisper-aligns the FINAL VO and writes `beats.json` — one row per beat
with exact start/end. All cuts and captions derive from this. Never time
anything by ear, and never re-time from the pre-1.3x audio.

### Stage 6 — EDL: panel picks + crops (YOU write it; software validates)

Write `projects/<project>/shorts/short<N>/edl.json`:

```json
{"beats": {
  "B01": {"panel": "P040-02", "crop": [x0, y0, x1, y1], "motion": "push_in"},
  "END": {"panel": "P003-01", "crop": [...], "motion": "static"}
}}
```

One entry per beat id in `beats.json`, plus `END`.

How to pick:

- View the contact sheets (`media/chN/sheets/`) to find candidate panels,
  then view each candidate as a SINGLE panel image before committing to it.
  Never judge a panel from a sheet thumbnail alone, and never trust the
  OCR text to tell you what a panel shows.
- One panel per beat: reaction face for emotional beats, the action panel
  for reveals, the widest panel for scene-setting. The panel must depict
  the beat's subject — right character, right action.
- **Crops are fractions of the single panel.** The crop's pixel aspect
  (width fraction × panel width ÷ height fraction × panel height) must be
  9:16 within 0.5% — the validator will reject anything else. A reliable
  method: choose a center (cx, cy) and a width fraction wf; the height
  fraction is then `wf × panel_w / (0.5625 × panel_h)`; clamp inside the
  panel.
- Keep faces whole inside the crop. Exclude speech bubbles and site
  watermarks where the geometry allows; NEVER pick a panel where a
  shouting face is combined with a dominant speech bubble (it renders as
  a grey-mask blob) — pick another panel or crop the face with the bubble
  excluded.
- Motions: `push_in` (default; reveals, faces), `push_in_slow`,
  `pull_out` (gods appearing, scale reveals), `pan_down` / `pan_up` /
  `pan_right` / `pan_left` (scene panels), `static_shake` (impacts —
  the slash), `static` (the END freeze).
- If a panel's own text (system windows) is wider than 9:16, edge letters
  will clip — that is geometry, not an error; the caption carries the
  meaning. You may add `"caption_y": 1330` to a beat's EDL entry to move
  its caption into a dark zone instead of over the panel's own text.
- Exception: if a joke/beat genuinely needs a whole wide panel, use
  `"crop": [0,0,1,1], "whole": true` — it renders whole on a blurred
  backdrop. At most one per short.
- The `END` entry is the freeze frame under the end card: pick the
  strongest cliffhanger frame.
- Only the ingested chapters' own panels. No outside art, ever. If a beat
  has no literal panel (it happens — e.g. an event described but not
  drawn), use the closest reaction-grade panel and note it in your report;
  never fake a scene with an unrelated panel.

Validate (fix and re-run until clean):

```bash
.venv/bin/python -m shorts_builder.cli edl <project> short<N>
```

### Stage 7 — Render + QC + posting pack (software; you verify)

```bash
.venv/bin/python -m shorts_builder.cli render <project> short<N>
```

Renders per-beat motion segments (cached — re-renders after an EDL fix
only redo the changed beats), burns Anton captions, mixes the VO with a
ducked synthesized music bed + sting/riser at the `[music]` beats, muxes
to `shorts/short<N>/out/<Series>_Short_v<K>.mp4` (always a fresh filename),
then runs QC and writes `posting_pack.md` (title, description, hashtags,
pinned comment = the end question).

**Your verification (mandatory):** open `shorts/short<N>/build/
qc_frames.png` — the first frame of every cut — and check:

- no sliced faces, no cut-off heads;
- no grey-mask blobs, no dominant bubbles over faces;
- captions readable everywhere (not lost over bright art or panel text);
- the hook frame (B01) is a strong face/action panel with the hook caption;
- the END card text is legible.

If a frame fails, fix the EDL (that beat's panel/crop/`caption_y`), delete
that beat's cached segment (`build/seg_<beat>.mp4`), and re-run render.
Deliver only when the frame sheet is clean.

## 3. Deliver

Report to the user, per short:

- the mp4 itself (attach it),
- duration + beat count,
- the posting pack contents,
- an honest residue list (any frame that is a compromise, and why).

## 4. Hard rules (never break)

- 9:16, 1080×1920, 30fps; 45–100s. VO pace is 1.3x baked into synthesis;
  ALL timings measured on the final 1.3x audio.
- Only the chapters' own panels. No outside art.
- No grey-mask panels (shouting face + dominant bubble).
- Measure every crop on the single panel image, never on a composite.
- Fresh filename for every render; never overwrite a delivered file.
- The font is the bundled Anton (`assets/fonts/Anton-Regular.ttf`).
  Do not substitute another font.
- Never print or commit the Deepgram key.

## 5. Known failure modes (already fixed in code — don't re-debug)

- Whisper needs 16kHz mono (the beats stage resamples automatically).
- ffmpeg `crop` uses frame variable `n`; `zoompan` uses `on`.
- `adelay` for mono SFX takes a single delay value.
- If the final mix isn't padded to the full beat length, `-shortest`
  truncates the end card — the renderer pads it; don't remove that.
- Cold renders are slow (~10 min for ~26 beats on a small VM). Segments
  are cached; fix cycles are ~1 min. Don't restart a render from scratch
  to fix one beat — delete only that beat's segment.
