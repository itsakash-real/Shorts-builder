# Shorts Builder

Standalone product that turns manhwa chapters into viral-style vertical shorts.

**Input:** one or more chapter links (AsuraScans) + how many shorts you want.
**Output:** finished 9:16 shorts (1080×1920, ~45–100s) + a posting pack
(title, description, hashtags, pinned comment) per short.

The output standard is the reference build "Solo Swordmaster Short #1 —
The world's strongest man is broke" (54.8s, 26 beats), produced manually on
2026-10-22. Its beat sheet and edit decision list are kept in
`examples/short1-golden/` as the ground-truth target this software reproduces.

## Pipeline (7 stages)

1. **Ingest** — fetch chapter pages from the links, extract panels.
2. **Understand** — panel transcript (OCR + vision notes) → story summary.
3. **Script** — write N short scripts in the locked house style
   (`docs/SCRIPT_STYLE.md`): hook-first breathless chain, `[music]` cues,
   cliffhanger ending, end-card question.
4. **Voice-over** — Deepgram per-sentence TTS at native speed 1.3x, joined,
   loudness-normalized; whisper transcript gate (no dropped/garbled lines).
5. **Beat sheet** — whisper-align the final 1.3x VO → word timestamps →
   one row per clause (text, start, end). All cuts/captions derive from this.
6. **EDL + render** — one panel per beat, exact 9:16 crop measured on the
   single panel, motion per beat (push-in / pan / static-shake / pull-out),
   manual ffmpeg segments; music bed + stings synthesized, ducked under VO.
   Review gate: the EDL is approved before rendering.
7. **Captions + QC + deliver** — bold ALL-CAPS captions (bundled Anton font,
   thick stroke + shadow, hook words in yellow/red), cliffhanger freeze +
   series name + end question; QC gates (sync spot-check, mute test,
   hook test, first-frame-of-every-cut, audio, file spec); fresh filename
   per render; posting pack emitted alongside the mp4.

## Hard rules (from the reference build — non-negotiable)

- 9:16, 1080×1920, 30fps; target length 45–100s.
- VO pace is 1.3x baked into synthesis; ALL timings measured on the final
  1.3x audio, never before.
- Only the chapters' own panels. No outside art.
- No grey-mask panels (shouting face + dominant speech bubble): drop or
  crop the face with the bubble excluded.
- Measure every crop on the single panel image, never on a composite sheet.
- Fresh filename for every render.

## Status

**Working end-to-end (v0.1).** All stages are implemented in
`shorts_builder/` (ingest, understand/OCR, script validation, VO, beats,
EDL validation, renderer, QC, posting pack). Verified 2026-10-23 with a
full run on Solo Swordmaster ch1 — link in, finished short out
(52.1s, 1080×1920, QC spec PASS); the worked example (script, EDL, beats,
posting pack) lives in `projects/test-solo/`.

Usage:
```
python -m shorts_builder.cli new <project> --chapters <url...>
python -m shorts_builder.cli understand <project> --chapter 1
# agent writes shorts/<short>/script.json (docs/SCRIPT_STYLE.md)
python -m shorts_builder.cli vo <project> <short>
python -m shorts_builder.cli beats <project> <short>
# agent writes shorts/<short>/edl.json (panel + exact 9:16 crop + motion per beat)
python -m shorts_builder.cli render <project> <short>   # render + QC + posting pack
```
Known v1 limits: renders are not fast (~10 min cold for 26 beats on a
small VM; segments are cached, re-renders are ~1 min); the script and
EDL stages are agent-driven by design (same pattern as the MahwaOCR
product) — the software validates both against hard contracts.
