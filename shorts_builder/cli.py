"""Shorts Builder CLI: new -> understand -> script -> vo -> beats -> edl -> render -> qc."""
import argparse
import json

from . import beats as beats_mod
from . import edl as edl_mod
from . import ingest as ingest_mod
from . import qc as qc_mod
from . import render as render_mod
from . import script as script_mod
from . import understand as understand_mod
from . import vo as vo_mod
from .project import ensure_project, project_dir


def main() -> None:
    ap = argparse.ArgumentParser(prog="shorts", description="Manhwa Shorts Builder")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new"); p.add_argument("project")
    p.add_argument("--chapters", nargs="+", required=True,
                   help="chapter URLs in order")
    p = sub.add_parser("understand"); p.add_argument("project")
    p.add_argument("--chapter", type=int, default=1)
    p = sub.add_parser("script"); p.add_argument("project"); p.add_argument("short")
    p = sub.add_parser("vo"); p.add_argument("project"); p.add_argument("short")
    p = sub.add_parser("beats"); p.add_argument("project"); p.add_argument("short")
    p = sub.add_parser("edl"); p.add_argument("project"); p.add_argument("short")
    p.add_argument("--chapter", type=int, default=1)
    p = sub.add_parser("render"); p.add_argument("project"); p.add_argument("short")
    p.add_argument("--chapter", type=int, default=1)
    p.add_argument("--no-bgm", action="store_true",
                   help="voice-only mix: no music bed, no stings (owner adds music)")
    p.add_argument("--bgm", default=None,
                   help="path to a YouTube Audio Library track: looped, "
                        "ducked low under the voice (daily-run mode)")
    p = sub.add_parser("qc"); p.add_argument("project"); p.add_argument("short")
    p = sub.add_parser("build"); p.add_argument("project"); p.add_argument("short")
    p.add_argument("--chapter", type=int, default=1)
    p.add_argument("--no-bgm", action="store_true",
                   help="voice-only mix: no music bed, no stings (owner adds music)")
    p.add_argument("--bgm", default=None,
                   help="path to a YouTube Audio Library track: looped, "
                        "ducked low under the voice (daily-run mode)")
    a = ap.parse_args()
    proj = ensure_project(a.project) if a.cmd == "new" else project_dir(a.project)

    if a.cmd == "new":
        for i, url in enumerate(a.chapters, 1):
            m = ingest_mod.ingest(proj, url, i)
            print(f"ch{i}: {m['pages']} pages, {len(m['panels'])} panels")
    elif a.cmd == "understand":
        out = understand_mod.ocr_chapter(proj, a.chapter)
        sdir = understand_mod.contact_sheets(proj, a.chapter)
        print(f"OCR -> {out}; sheets -> {sdir}")
    elif a.cmd in ("script", "vo", "beats", "edl", "render", "qc", "build"):
        s = script_mod.load(proj, a.short)
        errs = script_mod.validate(s)
        if errs:
            raise SystemExit("SCRIPT INVALID:\n- " + "\n- ".join(errs))
        if a.cmd == "script":
            print("script valid")
            return
        if a.cmd in ("vo", "build"):
            vo = vo_mod.build_vo(proj, a.short, s)
            print(f"VO -> {vo}")
            if a.cmd == "vo":
                return
        beats_path = proj / "shorts" / a.short / "beats.json"
        if a.cmd in ("beats", "build"):
            beats_path = beats_mod.build_beats(proj, a.short, s)
            print(f"beats -> {beats_path}")
            if a.cmd == "beats":
                return
        beats = json.loads(beats_path.read_text())["beats"]
        e = edl_mod.load(proj, a.short)
        errs = edl_mod.validate(proj, a.chapter, beats, e)
        if errs:
            raise SystemExit("EDL INVALID:\n- " + "\n- ".join(errs))
        if a.cmd == "edl":
            print("EDL valid")
            return
        if a.no_bgm and a.bgm:
            raise SystemExit("--no-bgm and --bgm are mutually exclusive")
        out = render_mod.render(proj, a.short, a.chapter, s, beats, e,
                                no_bgm=a.no_bgm, bgm=a.bgm)
        print(f"rendered -> {out}")
        rep = qc_mod.qc(proj, a.short, beats, out)
        print("QC:", json.dumps(rep["checks"]))
        pack = qc_mod.posting_pack(proj, a.short, s, out)
        print(f"posting pack -> {pack}")


if __name__ == "__main__":
    main()
