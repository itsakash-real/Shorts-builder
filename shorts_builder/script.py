"""Script contract + validation.

script.json (written by the agent, per docs/SCRIPT_STYLE.md):
{
 "series": "Solo Swordmaster", "title": "...", "hook_caption": "...",
 "end_question": "...", "hashtags": ["#manhwa", ...],
 "sentences": [
   {"text": "spoken sentence (a comma chain of clauses)",
    "beats": [{"caption": "ALL CAPS CHUNK", "highlight": ["WORD"], "music": null}]}
 ]
}
Beat captions within a sentence partition its clauses in order.
"""
import json
from pathlib import Path

WORDS_PER_SEC = 3.55  # calibrated on the golden build: ~200 words -> ~53s speech at 1.3x


def load(project: Path, short: str) -> dict:
    return json.loads((project / "shorts" / short / "script.json").read_text())


def validate(s: dict) -> list[str]:
    errs = []
    if not s.get("hook_caption"):
        errs.append("missing hook_caption")
    if not s.get("end_question"):
        errs.append("missing end_question")
    total_words = 0
    nbeats = 0
    for i, sent in enumerate(s.get("sentences", []), 1):
        w = len(sent["text"].split())
        total_words += w
        if w > 22:
            errs.append(f"sentence {i}: {w} words (>22) — split it; shorts stay lean "
                        "(user directive 2026-10-24: too many words)")
        if not sent.get("beats"):
            errs.append(f"sentence {i}: no beats")
        for b in sent.get("beats", []):
            nbeats += 1
            if len(b["caption"].split()) > 8:
                errs.append(f"sentence {i}: caption too long: {b['caption']!r}")
    est = total_words / WORDS_PER_SEC
    if not (28 <= est <= 60):
        errs.append(f"estimated VO {est:.0f}s outside 28–60s target band — "
                    "cut words; lean scripts only (user directive 2026-10-24)")
    if nbeats < 12:
        errs.append(f"only {nbeats} beats — shorts need dense cuts (min 12)")
    return errs
