# Shorts Builder — Product Spec v0.1

## User story
User pastes manhwa chapter link(s) and asks for N shorts.
The software produces N finished shorts + posting packs, matching the
reference build (examples/short1-golden/) in style, pacing and QC.

## CLI shape (target)
```
shorts new <project> --chapters <url...>      # ingest + understand
shorts script <project> --count N             # write N scripts (style-locked)
shorts produce <project> <shortN>             # VO → beats → EDL (gate) → render → QC → deliver
shorts build <project> --count N              # all of the above
```

## Stage contracts
- **Ingest**: chapter page HTML → image strips (strict `[a-f0-9]{6}\.webp`
  pattern; entry #1 is a credits banner, excluded from panels) → panels
  sliced per the series' panel rules. Deterministic; no AI.
- **Understand**: per-panel OCR text + vision description → chapter
  transcript + summary. AI step (agent-driven; prompts ship in `prompts/`).
- **Script**: N scripts per docs/SCRIPT_STYLE.md. AI step. Each script:
  hook line, beat chain, `[music]` cues, end question, series-name outro.
- **VO**: Deepgram, per sentence, native speed 1.3 (fallback: 1.0 +
  pitch-preserved atempo=1.3 — one method per short, recorded). Join with
  ~120ms gaps, loudness-normalize. Gate: whisper transcript diff vs script.
- **Beats**: whisper-align FINAL VO → word timestamps → beats.md
  (sentence windows exact; intra-sentence clause splits word-proportional).
- **EDL**: per beat — panel id, crop box (fractions of the single panel,
  aspect exactly 9:16 ±0.5%), motion, caption chunk. Gate (human/agent
  review): subject match, faces whole, no mask-risk panels, no watermarks,
  last panel = strongest cliffhanger frame. Known renderer lessons baked in:
  PIL textlength underestimates at large sizes → auto-fit captions to
  ≤1010px; ffmpeg tremolo f ≥ 0.1; sine source rejects time expressions →
  use aevalsrc phase integrals for sweeps/risers.
- **Render**: per-beat ffmpeg segments → concat; music bed synthesized,
  ducked under VO; sting/riser/swell at `[music]` points; captions as PNG
  overlays in bundled Anton (assets/fonts/Anton-Regular.ttf, OFL) with
  thick stroke + shadow, hook words yellow/red; end card = freeze +
  series name + question + "Full story on the channel".
- **QC gates** (all must pass): sync spot-check ≤0.1s; mute test; hook
  test (first 2s); first frame of every cut inspected; audio clarity;
  file = 1080×1920, duration = VO + end card, fresh filename.
- **Deliver**: mp4 + posting pack (title, description w/ end question,
  hashtags, pinned comment = end question).

## Non-goals (v1)
- No GUI. No long-form chapter videos (that is the MahwaOCR product).
- No outside art, no other series' panels.

## Open decisions
- Fully-automatic script/EDL via a model API vs agent-driven stages
  (MahwaOCR pattern). v1 ships agent-driven prompts + deterministic code
  for everything else; API automation can slot behind the same contracts.
