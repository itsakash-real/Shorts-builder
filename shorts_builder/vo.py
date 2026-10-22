"""VO: Deepgram per-sentence TTS at native speed 1.3, joined + loudness-normalized.

Key: env DEEPGRAM_API_KEY or ~/.config/manhwa/deepgram.key (never logged/stored).
"""
import json
import os
import subprocess
import urllib.request
from pathlib import Path

MODEL = "aura-2-orion-en"
SPEED = 1.3
GAP_MS = 120


def _key() -> str:
    if os.environ.get("DEEPGRAM_API_KEY"):
        return os.environ["DEEPGRAM_API_KEY"].strip()
    return Path("~/.config/manhwa/deepgram.key").expanduser().read_text().strip()


def synth_sentence(text: str, out_wav: Path):
    body = json.dumps({"text": text}).encode()
    url = (f"https://api.deepgram.com/v1/speak?model={MODEL}"
           f"&encoding=linear16&sample_rate=24000&speed={SPEED}")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": f"Token {_key()}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        out_wav.write_bytes(r.read())


def build_vo(project: Path, short: str, script: dict) -> Path:
    sdir = project / "shorts" / short
    vod = sdir / "vo"
    vod.mkdir(parents=True, exist_ok=True)
    wavs = []
    for i, sent in enumerate(script["sentences"], 1):
        w = vod / f"s{i:02d}.wav"
        if not w.exists():
            synth_sentence(sent["text"], w)
        wavs.append(w)
    gap = vod / "gap.wav"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i",
                    "anullsrc=r=24000:cl=mono", "-t", str(GAP_MS / 1000),
                    str(gap)], check=True, capture_output=True)
    concat = vod / "concat.txt"
    parts = []
    for w in wavs:
        parts.append(f"file '{w.name}'")
        parts.append(f"file 'gap.wav'")
    concat.write_text("\n".join(parts[:-1]) + "\n")
    raw = vod / "vo_raw.wav"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
                    str(concat), "-c", "copy", str(raw)],
                   check=True, capture_output=True)
    final = vod / "vo_final.wav"
    subprocess.run(["ffmpeg", "-y", "-i", str(raw), "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "24000",
                    str(final)], check=True, capture_output=True)
    return final
