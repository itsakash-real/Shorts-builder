"""QC: file spec + first-frame-of-every-cut contact sheet + report."""
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json",
                          "-show_format", "-show_streams", str(path)],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    return {"width": v["width"], "height": v["height"],
            "duration": float(d["format"]["duration"])}


def qc(project: Path, short: str, beats: list, video: Path) -> dict:
    sdir = project / "shorts" / short
    spec = probe(video)
    checks = {"spec_1080x1920": spec["width"] == 1080 and spec["height"] == 1920,
              "duration_matches_beats": abs(spec["duration"] - beats[-1]["end"]) < 1.5}
    thumbs = []
    for b in beats:
        f = sdir / "build" / f"qc_{b['id']}.png"
        subprocess.run(["ffmpeg", "-y", "-ss", f"{min(b['start'] + 0.05, spec['duration'] - 0.2):.2f}",
                        "-i", str(video), "-frames:v", "1", str(f)],
                       capture_output=True)
        im = Image.open(f).convert("RGB")
        im.thumbnail((270, 480))
        thumbs.append((b["id"], im))
    cols = 5
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 274, rows * 500), "white")
    d = ImageDraw.Draw(sheet)
    for i, (bid, im) in enumerate(thumbs):
        x, y = (i % cols) * 274, (i // cols) * 500
        sheet.paste(im, (x + 2, y + 18))
        d.text((x + 4, y + 2), bid, fill=(200, 0, 0))
    sheet_path = sdir / "build" / "qc_frames.png"
    sheet.save(sheet_path)
    report = {"file": str(video), **spec, "checks": checks,
              "frames_sheet": str(sheet_path)}
    (sdir / "qc_report.json").write_text(json.dumps(report, indent=1))
    return report


def posting_pack(project: Path, short: str, script: dict, video: Path) -> Path:
    sdir = project / "shorts" / short
    tags = " ".join(script.get("hashtags", ["#manhwa", "#manhwarecap", "#shorts"]))
    text = (f"# Posting pack — {short}\n\n"
            f"**File:** {video.name}\n\n"
            f"**Title:** {script['title']}\n\n"
            f"**Description:**\n{script['end_question']}\n"
            f"Full story on the channel — {script['series']}.\n{tags}\n\n"
            f"**Pinned comment:** {script['end_question']}\n")
    p = sdir / "posting_pack.md"
    p.write_text(text)
    return p
