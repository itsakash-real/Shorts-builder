"""Renderer: beats + EDL -> 1080x1920 mp4 (manual ffmpeg, golden method).

Per beat: PIL crop -> 2160x3840 canvas -> ffmpeg motion segment ->
caption PNG overlay (bundled Anton, stroke+shadow, hook words yellow).
Audio: VO + synthesized ducked music bed + sting/riser at [music] points.
End card: freeze + series name + end question.
"""
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets" / "fonts" / "Anton-Regular.ttf"
W, H, FPS = 1080, 1920, 30
YELLOW = (255, 216, 0)
RED = (255, 59, 48)
WHITE = (255, 255, 255)


def _run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def _font(size):
    return ImageFont.truetype(str(FONT), size)


def _wrap(text, font, max_w, draw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def caption_png(text, highlights, path, big=False):
    img = Image.new("RGBA", (W, 700), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = 120 if big else 96
    while size > 30:
        f = _font(size)
        lines = _wrap(text, f, 1010, d)
        if max(d.textlength(l, font=f) for l in lines) <= 1010 and len(lines) <= 3:
            break
        size -= 6
    f = _font(size)
    lines = _wrap(text, f, 1010, d)
    lh = int(size * 1.12)
    y = (700 - lh * len(lines)) // 2
    for line in lines:
        words = line.split()
        widths = [d.textlength(w, font=f) for w in words]
        space = d.textlength(" ", font=f)
        x = (W - (sum(widths) + space * (len(words) - 1))) / 2
        for w, wd in zip(words, widths):
            color = YELLOW if w.strip(".,!?") in highlights else WHITE
            d.text((x + 4, y + 5), w, font=f, fill=(0, 0, 0))
            d.text((x, y), w, font=f, fill=color, stroke_width=7,
                   stroke_fill=(0, 0, 0))
            x += wd + space
        y += lh
    img.save(path)


def endcard_png(series, question, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 900, W, 1560], fill=(0, 0, 0, 150))
    f1 = _font(118)
    lines = _wrap(series.upper(), f1, 1000, d)
    y = 960
    for l in lines:
        d.text(((W - d.textlength(l, font=f1)) / 2, y), l, font=f1,
               fill=YELLOW, stroke_width=8, stroke_fill=(0, 0, 0))
        y += 132
    f2 = _font(74)
    y += 30
    for l in _wrap(question.upper(), f2, 980, d):
        d.text(((W - d.textlength(l, font=f2)) / 2, y), l, font=f2,
               fill=WHITE, stroke_width=7, stroke_fill=(0, 0, 0))
        y += 86
    f3 = _font(44)
    t = "FULL STORY ON THE CHANNEL"
    d.text(((W - d.textlength(t, font=f3)) / 2, y + 36), t, font=f3,
           fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0))
    img.save(path)


def crop_image(project, panel_file, crop, whole, out):
    im = Image.open(project / panel_file).convert("RGB")
    if whole:
        bg = im.resize((2160, 3840), Image.LANCZOS).filter(
            ImageFilter.GaussianBlur(60))
        fg = im.copy()
        fg.thumbnail((2000, 3560), Image.LANCZOS)
        bg.paste(fg, ((2160 - fg.width) // 2, (3840 - fg.height) // 2))
        bg.save(out)
    else:
        x0, y0, x1, y1 = crop
        box = (int(x0 * im.width), int(y0 * im.height),
               int(x1 * im.width), int(y1 * im.height))
        im.crop(box).resize((2160, 3840), Image.LANCZOS).save(out)


def motion_filter(motion, dur):
    frames = max(1, int(dur * FPS))
    if motion in ("push_in", "push_in_slow"):
        amt = 0.10 if motion == "push_in" else 0.05
        return (f"zoompan=z='1+{amt}*on/{frames}':x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}")
    if motion == "pull_out":
        return (f"zoompan=z='1.12-0.12*on/{frames}':x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}")
    if motion == "pan_down":
        return (f"crop=w=iw:h=ih*0.84:x=0:y='(ih-oh)*n/{frames}',"
                f"scale={W}:{H}")
    if motion == "pan_up":
        return (f"crop=w=iw:h=ih*0.84:x=0:y='(ih-oh)*(1-n/{frames})',"
                f"scale={W}:{H}")
    if motion == "pan_right":
        return (f"crop=w=iw*0.84:h=ih:x='(iw-ow)*n/{frames}':y=0,"
                f"scale={W}:{H}")
    if motion == "pan_left":
        return (f"crop=w=iw*0.84:h=ih:x='(iw-ow)*(1-n/{frames})':y=0,"
                f"scale={W}:{H}")
    if motion == "static_shake":
        return (f"crop=w=iw*0.96:h=ih*0.96:x='(iw-ow)/2+7*sin(2*PI*t*9)':"
                f"y='(ih-oh)/2+7*cos(2*PI*t*11)',scale={W}:{H}")
    return f"scale={W}:{H}"


def synth_audio(build: Path):
    # music bed: dark minor pad, slow tremolo (f>=0.1 per renderer lesson)
    _run(["ffmpeg", "-y", "-f", "lavfi", "-i",
          "aevalsrc=0.20*sin(2*PI*110*t)+0.14*sin(2*PI*165*t)+"
          "0.10*sin(2*PI*220*t):s=44100", "-af", "tremolo=f=0.1:d=0.4,"
          "lowpass=f=900", "-t", "130", str(build / "bed.wav")])
    # riser: phase-integral frequency sweep (sine source rejects time exprs)
    _run(["ffmpeg", "-y", "-f", "lavfi", "-i",
          "aevalsrc=0.25*sin(2*PI*(180*t+160*t*t)):s=44100", "-t", "1.6",
          str(build / "riser.wav")])
    # hit: sine drop + noise burst
    _run(["ffmpeg", "-y", "-f", "lavfi", "-i",
          "aevalsrc=0.5*sin(2*PI*(300*t-120*t*t)):s=44100", "-t", "0.5",
          str(build / "hit.wav")])


def render(project: Path, short: str, chapter_no: int, script: dict,
           beats: list, edl: dict, no_bgm: bool = False,
           bgm: str = None) -> Path:
    sdir = project / "shorts" / short
    build = sdir / "build"
    build.mkdir(exist_ok=True)
    media = project / "media" / f"ch{chapter_no}"
    manifest = json.loads((media / "panels.json").read_text())
    panels = {p["id"]: p for p in manifest["panels"]}
    segs = []
    for b in beats:
        e = edl["beats"][b["id"]]
        dur = b["end"] - b["start"]
        canvas = build / f"img_{b['id']}.png"
        crop_image(project, panels[e["panel"]]["file"], e["crop"],
                   e.get("whole", False), canvas)
        seg = build / f"seg_{b['id']}.mp4"
        if seg.exists():
            segs.append(seg)
            continue
        vf = motion_filter(e["motion"], dur)
        if b["id"] == "END":
            cap = build / "cap_END.png"
            endcard_png(script["series"], script["end_question"], cap)
            vf += f",overlay=0:0"
            _run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(canvas), "-i",
                  str(cap), "-filter_complex", vf, "-t", f"{dur:.2f}",
                  "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                  str(seg)])
        else:
            cap = build / f"cap_{b['id']}.png"
            caption_png(b["caption"], [h.upper() for h in b["highlight"]], cap)
            y = e.get("caption_y", 560)
            vf += f",overlay=0:{y}"
            inputs = ["-loop", "1", "-framerate", str(FPS), "-i", str(canvas), "-i", str(cap)]
            if b["id"] == "B01":
                hook = build / "cap_HOOK.png"
                caption_png(script["hook_caption"], [], hook, big=True)
                inputs += ["-i", str(hook)]
                vf += ",overlay=0:120"
            _run(["ffmpeg", "-y", *inputs, "-filter_complex", vf,
                  "-t", f"{dur:.2f}", "-r", str(FPS), "-c:v", "libx264",
                  "-pix_fmt", "yuv420p", str(seg)])
        segs.append(seg)
    concat = build / "concat.txt"
    concat.write_text("\n".join(f"file '{s.name}'" for s in segs) + "\n")
    video = build / "video.mp4"
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
          "-c", "copy", str(video)])
    total = beats[-1]["end"]
    if bgm:
        # LIBRARY-BGM mode (user directive 2026-10-24): a real track from
        # the YouTube Audio Library (assets/bgm/), looped to length, faded
        # out at the end, and mixed LOW under the voice (sidechain-ducked,
        # ~-19 dB under VO) — the narration must always stay clearly
        # audible. No synthesized bed, no synth stings: the track carries
        # the energy.
        fade_st = max(0.0, total - 1.5)
        inputs = ["-i", str(sdir / "vo" / "vo_final.wav"),
                  "-stream_loop", "-1", "-i", str(bgm)]
        filters = ["[0:a]aresample=44100[vo]",
                   f"[1:a]aresample=44100,atrim=0:{total:.2f},"
                   f"afade=t=out:st={fade_st:.2f}:d=1.5,volume=0.16[bedraw]",
                   "[bedraw][vo]sidechaincompress=threshold=0.03:ratio=8:"
                   "attack=40:release=400[bed]",
                   "[vo][bed]amix=inputs=2:duration=first:normalize=0[mix]",
                   f"[mix]apad=whole_dur={total:.2f},atrim=0:{total:.2f},"
                   "loudnorm=I=-14:TP=-1.5:LRA=11[aout]"]
    elif no_bgm:
        # NO-BGM mode (user directive 2026-10-24): voice-only mix — no music
        # bed and no sting/riser layers; the owner adds music themselves.
        inputs = ["-i", str(sdir / "vo" / "vo_final.wav")]
        filters = ["[0:a]aresample=44100[vo]",
                   f"[vo]apad=whole_dur={total:.2f},atrim=0:{total:.2f},"
                   "loudnorm=I=-14:TP=-1.5:LRA=11[aout]"]
    else:
        synth_audio(build)
        inputs = ["-i", str(sdir / "vo" / "vo_final.wav"), "-i",
                  str(build / "bed.wav")]
        filters = ["[0:a]aresample=44100[vo]",
                   "[1:a]atrim=0:" + f"{total:.2f}" + ",volume=0.5[bedraw]",
                   "[bedraw][vo]sidechaincompress=threshold=0.03:ratio=8:"
                   "attack=40:release=400[bed]",
                   "[vo][bed]amix=inputs=2:duration=first:normalize=0[mix]"]
        cur, n = "mix", 2
        for b in beats:
            if b.get("music") in ("sting", "shift", "swell"):
                src_name = "hit.wav" if b["music"] == "sting" else "riser.wav"
                inputs += ["-i", str(build / src_name)]
                ms = int(b["start"] * 1000)
                filters.append(f"[{n}:a]adelay={ms},volume=0.7[s{n}]")
                filters.append(f"[{cur}][s{n}]amix=inputs=2:duration=first:"
                               f"normalize=0[mix{n}]")
                cur = f"mix{n}"
                n += 1
        filters.append(f"[{cur}]apad=whole_dur={total:.2f},atrim=0:{total:.2f},loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    mix = build / "mix.m4a"
    _run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters),
          "-map", "[aout]", str(mix)])
    outdir = sdir / "out"
    outdir.mkdir(exist_ok=True)
    k = 1
    while True:
        name = f"{script['series'].replace(' ', '_')}_Short_v{k}.mp4"
        out = outdir / name
        if not out.exists():
            break
        k += 1
    _run(["ffmpeg", "-y", "-i", str(video), "-i", str(mix), "-c:v", "copy",
          "-c:a", "aac", "-shortest", str(out)])
    return out
