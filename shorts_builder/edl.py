"""EDL contract + validation.

edl.json (written by the agent after viewing panels/sheets):
{"beats": {"B01": {"panel": "P002-01", "crop": [x0,y0,x1,y1], "motion": "push_in"},
           "END": {"panel": "...", "crop": [...], "motion": "static"}}}
Crop fractions are of the SINGLE panel. Pixel aspect must be 9:16 (±0.5%),
unless "whole": true (whole panel on blurred backdrop — the plaque exception).
"""
import json
from pathlib import Path

MOTIONS = {"push_in", "push_in_slow", "pull_out", "pan_down", "pan_up",
           "pan_right", "pan_left", "static", "static_shake"}
TARGET = 1080 / 1920


def load(project: Path, short: str) -> dict:
    return json.loads((project / "shorts" / short / "edl.json").read_text())


def validate(project: Path, chapter_no: int, beats: list, edl: dict) -> list[str]:
    media = project / "media" / f"ch{chapter_no}"
    manifest = json.loads((media / "panels.json").read_text())
    panels = {p["id"]: p for p in manifest["panels"]}
    errs = []
    for b in beats:
        e = edl.get("beats", {}).get(b["id"])
        if not e:
            errs.append(f"{b['id']}: missing EDL entry")
            continue
        p = panels.get(e["panel"])
        if not p:
            errs.append(f"{b['id']}: unknown panel {e['panel']}")
            continue
        if e["motion"] not in MOTIONS:
            errs.append(f"{b['id']}: bad motion {e['motion']}")
        if not e.get("whole"):
            x0, y0, x1, y1 = e["crop"]
            ratio = ((x1 - x0) * p["w"]) / max(1.0, (y1 - y0) * p["h"])
            if abs(ratio - TARGET) / TARGET > 0.005:
                errs.append(f"{b['id']}: crop aspect {ratio:.4f} != 9:16 "
                            f"(panel {e['panel']} {p['w']}x{p['h']})")
    return errs
