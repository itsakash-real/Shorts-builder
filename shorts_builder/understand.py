"""Understand: per-panel OCR text -> panels_ocr.json + contact sheets for the agent."""
import json
from pathlib import Path

from PIL import Image, ImageDraw


def ocr_chapter(project: Path, chapter_no: int) -> Path:
    from rapidocr_onnxruntime import RapidOCR
    engine = RapidOCR()
    media = project / "media" / f"ch{chapter_no}"
    manifest = json.loads((media / "panels.json").read_text())
    for p in manifest["panels"]:
        result, _ = engine(str(project / p["file"]))
        lines = []
        if result:
            lines = [t for _, t, conf in result if conf > 0.45]
        p["ocr"] = " ".join(lines)
    out = media / "panels_ocr.json"
    out.write_text(json.dumps(manifest, indent=1))
    return out


def contact_sheets(project: Path, chapter_no: int, per_sheet=12):
    """Grid sheets of panels with ids, for agent panel-picking."""
    media = project / "media" / f"ch{chapter_no}"
    manifest = json.loads((media / "panels.json").read_text())
    sdir = media / "sheets"
    sdir.mkdir(exist_ok=True)
    panels = manifest["panels"]
    for si in range(0, len(panels), per_sheet):
        chunk = panels[si:si + per_sheet]
        cols, tw, th = 3, 300, 340
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * th), "white")
        d = ImageDraw.Draw(sheet)
        for i, p in enumerate(chunk):
            im = Image.open(project / p["file"]).convert("RGB")
            im.thumbnail((tw - 8, th - 24))
            x, y = (i % cols) * tw, (i // cols) * th
            sheet.paste(im, (x + 4, y + 20))
            d.text((x + 6, y + 4), p["id"], fill=(200, 0, 0))
        sheet.save(sdir / f"sheet_{si // per_sheet + 1:02d}.png")
    return sdir
