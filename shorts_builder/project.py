"""Project layout: projects/<name>/ with media/, work/, shorts/."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def project_dir(name: str) -> Path:
    return ROOT / "projects" / name


def ensure_project(name: str) -> Path:
    p = project_dir(name)
    for sub in ("media", "work", "shorts"):
        (p / sub).mkdir(parents=True, exist_ok=True)
    return p
