"""Create your fellow file from your GitHub profile, once.

    python scripts/add_fellow.py <your-github-username>

This copies your name, bio and website from GitHub, saves your GitHub photo
into photos/, and writes fellows/<username>.yaml for you to edit.
Nothing is fetched again later: after this, the file is yours to change.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FELLOWS_DIR = ROOT / "fellows"
PHOTOS_DIR = ROOT / "photos"
API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "hodifellows-add-fellow"}


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def fetch_profile(username: str) -> dict:
    return fetch_json(f"{API}/users/{username}")


def download_photo(avatar_url: str, username: str) -> str:
    """Save the GitHub avatar as photos/<username>.jpg and return the file name."""
    PHOTOS_DIR.mkdir(exist_ok=True)
    name = f"{username.lower()}.jpg"
    request = urllib.request.Request(f"{avatar_url}&s=400" if "?" in avatar_url else f"{avatar_url}?s=400", headers=HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        (PHOTOS_DIR / name).write_bytes(response.read())
    return name


def build_entry(profile: dict, photo: str) -> dict:
    """Turn a GitHub profile into the fields of a fellow file."""
    username = profile["login"]
    links = {}
    blog = (profile.get("blog") or "").strip()
    if blog.startswith("https://"):
        links["website"] = blog
    return {
        "github": username,
        "name": profile.get("name") or username,
        "cohort": "Cohort 1 (2027)",
        "bio": (profile.get("bio") or "Write one or two sentences about yourself.").strip(),
        "photo": photo,
        "languages": [],
        "links": links,
        "testimonial": "",
        "consent": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create your fellow file from GitHub.")
    parser.add_argument("username", help="your GitHub username")
    args = parser.parse_args(argv)

    target = FELLOWS_DIR / f"{args.username.lower()}.yaml"
    if target.exists():
        print(f"{target.relative_to(ROOT)} already exists. Edit it directly.", file=sys.stderr)
        return 1
    try:
        profile = fetch_profile(args.username)
        photo = download_photo(profile["avatar_url"], profile["login"]) if profile.get("avatar_url") else ""
    except urllib.error.HTTPError as error:
        reason = "not found" if error.code == 404 else f"GitHub said {error.code}"
        print(f"Could not load '{args.username}' from GitHub: {reason}.", file=sys.stderr)
        return 1
    except urllib.error.URLError as error:
        print(f"Could not reach GitHub: {error.reason}", file=sys.stderr)
        return 1

    entry = build_entry(profile, photo)
    target.write_text(yaml.safe_dump(entry, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Created {target.relative_to(ROOT)}.")
    print("Next: open it, check every field, and set consent: true if you agree to be shown.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
