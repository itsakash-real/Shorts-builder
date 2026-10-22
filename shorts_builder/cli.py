"""CLI skeleton — stage subcommands land here as each stage is built."""
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="shorts", description="Manhwa Shorts Builder")
    sub = parser.add_subparsers(dest="command")
    p_new = sub.add_parser("new", help="ingest chapter links into a project")
    p_new.add_argument("project")
    p_new.add_argument("--chapters", nargs="+", required=True)
    p_script = sub.add_parser("script", help="write N style-locked scripts")
    p_script.add_argument("project")
    p_script.add_argument("--count", type=int, default=1)
    p_produce = sub.add_parser("produce", help="VO -> beats -> EDL -> render -> QC -> deliver")
    p_produce.add_argument("project")
    p_produce.add_argument("short")
    p_build = sub.add_parser("build", help="full pipeline")
    p_build.add_argument("project")
    p_build.add_argument("--count", type=int, default=1)
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    print(f"[shorts-builder] '{args.command}' stage — under construction (see SPEC.md)")


if __name__ == "__main__":
    main()
