"""Build the Hodi Fellows page from the files in fellows/.

Each fellow has one YAML file in fellows/ (see fellows/_template.yaml).
Only fellows with `consent: true` are published.

    python scripts/build.py                 # builds into _site/
    python scripts/build.py --out some/dir  # builds somewhere else
    python scripts/build.py --check         # only checks the files
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
FELLOWS_DIR = ROOT / "fellows"
PHOTOS_DIR = ROOT / "photos"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
DEFAULT_OUT = ROOT / "_site"

REQUIRED = ("github", "name", "cohort", "bio", "consent")
KNOWN_LINKS = ("portfolio", "linkedin", "website", "x", "blog")
GITHUB_USERNAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


@dataclass
class Fellow:
    github: str
    name: str
    cohort: str
    bio: str
    photo: str = ""
    languages: list[str] = field(default_factory=list)
    links: dict[str, str] = field(default_factory=dict)
    testimonial: str = ""

    @property
    def slug(self) -> str:
        return self.github.lower()

    @property
    def initials(self) -> str:
        parts = self.name.split()
        return "".join(p[0] for p in parts[:2]).upper()

    @property
    def github_url(self) -> str:
        return f"https://github.com/{self.github}"


class FellowError(Exception):
    """A problem in one fellow's file."""


def is_https_link(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def parse_fellow(path: Path) -> Fellow | None:
    """Read one fellow file. Returns None when the fellow hasn't consented."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise FellowError(f"{path.name}: not valid YAML ({error})") from error
    if not isinstance(data, dict):
        raise FellowError(f"{path.name}: should contain fields like 'name: Jane'")

    missing = [key for key in REQUIRED if data.get(key) in (None, "")]
    if missing:
        raise FellowError(f"{path.name}: missing {', '.join(missing)}")

    if data["consent"] is not True:
        return None

    github = str(data["github"]).strip()
    if not GITHUB_USERNAME.match(github):
        raise FellowError(f"{path.name}: '{github}' is not a valid GitHub username")
    if path.stem.lower() != github.lower():
        raise FellowError(f"{path.name}: the file should be named {github.lower()}.yaml")

    links = data.get("links") or {}
    if not isinstance(links, dict):
        raise FellowError(f"{path.name}: links should be a list of 'name: https://...' lines")
    clean_links = {}
    for key, value in links.items():
        if key not in KNOWN_LINKS:
            raise FellowError(f"{path.name}: unknown link '{key}' (use {', '.join(KNOWN_LINKS)})")
        if value in (None, ""):
            continue
        value = str(value).strip()
        if not is_https_link(value):
            raise FellowError(f"{path.name}: the {key} link must start with https://")
        clean_links[key] = value

    languages = data.get("languages") or []
    if not isinstance(languages, list):
        raise FellowError(f"{path.name}: languages should be a list, like [Python, JavaScript]")

    return Fellow(
        github=github,
        name=str(data["name"]).strip(),
        cohort=str(data["cohort"]).strip(),
        bio=str(data["bio"]).strip(),
        photo=str(data.get("photo") or "").strip(),
        languages=[str(lang).strip() for lang in languages if str(lang).strip()],
        links=clean_links,
        testimonial=str(data.get("testimonial") or "").strip(),
    )


def load_fellows(folder: Path = FELLOWS_DIR) -> list[Fellow]:
    """Load every fellow file, skipping ones that start with '_'."""
    fellows = []
    for path in sorted(folder.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        fellow = parse_fellow(path)
        if fellow:
            fellows.append(fellow)
    return fellows


def render(fellows: list[Fellow]) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env.get_template("index.html").render(fellows=fellows)


def build(out: Path, fellows: list[Fellow]) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "index.html").write_text(render(fellows), encoding="utf-8")
    shutil.copytree(STATIC_DIR, out / "static")
    used = {f.photo for f in fellows if f.photo}
    (out / "photos").mkdir()
    for name in used:
        source = PHOTOS_DIR / name
        if source.is_file():
            shutil.copy2(source, out / "photos" / name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Hodi Fellows page.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output folder")
    parser.add_argument("--check", action="store_true", help="check the files without building")
    args = parser.parse_args(argv)
    try:
        fellows = load_fellows()
    except FellowError as error:
        print(f"Problem found: {error}", file=sys.stderr)
        return 1
    if args.check:
        print(f"All good: {len(fellows)} fellow(s) will be shown.")
        return 0
    build(args.out, fellows)
    print(f"Built {args.out} with {len(fellows)} fellow(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
