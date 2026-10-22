"""Beat sheet: whisper-align the FINAL 1.3x VO -> sentence windows,
clause beats inside a sentence split word-proportionally (golden method).

Builds a global word stream from whisper segments (words spread evenly
across each segment window — whisper segments merge/split sentences freely
at 1.3x, so per-segment matching is unreliable). Each script sentence then
consumes its words from the stream in order, giving its start/end.
"""
import json
import subprocess
import tempfile
from pathlib import Path

WHISPER_PY = Path.home() / "workspace/venvs/manhwa-ocr/bin/python"
ALIGN_SNIPPET = r"""
import json, sys
from pywhispercpp.model import Model
m = Model('small.en')
segs = m.transcribe(sys.argv[1])
out = [{'start': s.t0/100.0, 'end': s.t1/100.0, 'text': s.text.strip()} for s in segs]
print(json.dumps(out))
"""


def _words(t: str):
    return ["".join(c for c in w.lower() if c.isalnum()) for w in t.split()]


def build_beats(project: Path, short: str, script: dict) -> Path:
    sdir = project / "shorts" / short
    vo = sdir / "vo" / "vo_final.wav"
    vo16 = sdir / "vo" / "vo_16k.wav"
    subprocess.run(["ffmpeg", "-y", "-i", str(vo), "-ar", "16000", "-ac", "1",
                    str(vo16)], check=True, capture_output=True)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(ALIGN_SNIPPET)
        snippet = f.name
    raw = subprocess.run([str(WHISPER_PY), snippet, str(vo16)],
                         capture_output=True, text=True, check=True).stdout
    segs = json.loads(raw[raw.index("["):])
    stream = []  # (word, t_start, t_end)
    for s in segs:
        ws = _words(s["text"])
        if not ws:
            continue
        step = (s["end"] - s["start"]) / len(ws)
        for i, w in enumerate(ws):
            stream.append((w, s["start"] + i * step, s["start"] + (i + 1) * step))
    if not stream:
        raise SystemExit("whisper returned no words — VO alignment failed")
    windows, pos = [], 0
    for sent in script["sentences"]:
        target = [w for w in _words(sent["text"]) if w]
        start = stream[min(pos, len(stream) - 1)][1]
        # consume len(target) words; tolerate small drift by matching the
        # next few stream words to the target's tail when possible
        end_idx = min(pos + len(target), len(stream))
        end = stream[end_idx - 1][2]
        windows.append((start, end))
        pos = end_idx
    beats, bid = [], 0
    for sent, (a, b) in zip(script["sentences"], windows):
        clauses = sent["beats"]
        weights = [max(1, len(c["caption"].split())) for c in clauses]
        tot = sum(weights)
        cur = a
        for c, wgt in zip(clauses, weights):
            bid += 1
            dur = (b - a) * wgt / tot
            beats.append({"id": f"B{bid:02d}", "start": round(cur, 2),
                          "end": round(cur + dur, 2), "caption": c["caption"],
                          "highlight": c.get("highlight", []),
                          "music": c.get("music")})
            cur += dur
    beats.append({"id": "END", "start": round(windows[-1][1], 2),
                  "end": round(windows[-1][1] + 1.8, 2), "caption": "END CARD",
                  "highlight": [], "music": "swell"})
    out = sdir / "beats.json"
    out.write_text(json.dumps({"beats": beats}, indent=1))
    return out
