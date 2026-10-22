"""Ingest: AsuraScans chapter URL -> downloaded page strips -> sliced panels.

Page data is embedded in the chapter page HTML as a flight payload:
"pages":[[0,{"url":[0,"https://cdn.../309026.webp"], "width":..., "height":...}], ...]
Entry #1 is a wide credits banner (skipped as a panel source but kept as page 1
in numbering, matching the reference pipeline's P001 = credits convention).
Panels are sliced from each strip at blank gutter rows.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
PAGE_RE = re.compile(
    r'\{&quot;url&quot;:\[0,&quot;(https://cdn\.asurascans\.com/asura-images/chapters/[^&]+?\.webp)(?:\?[^&]*)?&quot;\],'
    r'&quot;width&quot;:\[0,(\d+)\],&quot;height&quot;:\[0,(\d+)\]\}'
)


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def parse_pages(html: str):
    """Return [(url, width, height)] in reading order, deduped."""
    out, seen = [], set()
    for url, w, h in PAGE_RE.findall(html):
        if url not in seen:
            seen.add(url)
            out.append((url, int(w), int(h)))
    return out


def slice_panels(strip: np.ndarray, min_panel_h=140, min_gutter=6):
    """Split a tall strip (H,W,3) at blank gutter rows -> [(y0,y1)]."""
    gray = strip.mean(axis=(1, 2))
    spread = strip.std(axis=(1, 2))
    blank = ((gray > 243) | (gray < 12)) & (spread < 14)
    H = len(blank)
    runs, i = [], 0
    while i < H:
        if blank[i]:
            j = i
            while j < H and blank[j]:
                j += 1
            if j - i >= min_gutter:
                runs.append((i, j))
            i = j
        else:
            i += 1
    spans, prev = [], 0
    for g0, g1 in runs:
        if g0 - prev >= min_panel_h:
            spans.append((prev, g0))
        prev = max(prev, g1)
    if H - prev >= min_panel_h:
        spans.append((prev, H))
    elif spans:
        spans[-1] = (spans[-1][0], H)
    return spans


def ingest(project: Path, chapter_url: str, chapter_no: int) -> dict:
    html = fetch(chapter_url).decode("utf-8", "ignore")
    pages = parse_pages(html)
    if not pages:
        raise SystemExit(f"No chapter pages found at {chapter_url}")
    media = project / "media" / f"ch{chapter_no}"
    pdir = media / "panels"
    pdir.mkdir(parents=True, exist_ok=True)
    panels = []
    for pi, (url, w, h) in enumerate(pages, start=1):
        raw = fetch(url)
        tmp = media / f"page_{pi:03d}.webp"
        tmp.write_bytes(raw)
        if pi == 1:
            continue  # credits banner: kept for numbering, never a panel source
        img = np.asarray(Image.open(tmp).convert("RGB"))
        for si, (y0, y1) in enumerate(slice_panels(img), start=1):
            pid = f"P{pi:03d}-{si:02d}"
            out = pdir / f"{pid}.png"
            Image.fromarray(img[y0:y1]).save(out)
            panels.append({"id": pid, "page": pi, "y0": y0, "y1": y1,
                           "w": int(img.shape[1]), "h": int(y1 - y0),
                           "file": str(out.relative_to(project))})
    manifest = {"chapter": chapter_no, "source": chapter_url,
                "pages": len(pages), "panels": panels}
    (media / "panels.json").write_text(json.dumps(manifest, indent=1))
    return manifest


if __name__ == "__main__":
    from .project import ensure_project
    proj = ensure_project(sys.argv[1])
    m = ingest(proj, sys.argv[2], int(sys.argv[3]))
    print(f"pages={m['pages']} panels={len(m['panels'])}")
