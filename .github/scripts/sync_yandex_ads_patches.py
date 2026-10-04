"""
Mirrors the releases of nuc134r/yandex-ads-patches in the shape of the ReVanced API,
so ReVanced Manager can use this site as a patch bundle source:

- v5/patches/bundle.json: the latest release, used as the bundle URL
- v5/patches/history: all releases, used for the changelog
"""

import json
import os
import urllib.request
from pathlib import Path

REPOSITORY = "nuc134r/yandex-ads-patches"
OUTPUT = Path("v5/patches")


def get_releases():
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPOSITORY}/releases?per_page=100",
        headers={"Accept": "application/vnd.github+json"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(request) as response:
        return json.load(response)


def created_at(release):
    # ReVanced Manager parses a local date time without the zone designator.
    return release["published_at"].removesuffix("Z")


def main():
    releases = [
        release
        for release in get_releases()
        if not release["draft"] and not release["prerelease"]
    ]
    if not releases:
        raise SystemExit("No releases found")

    latest = releases[0]
    patches = next(asset for asset in latest["assets"] if asset["name"].endswith(".rvp"))

    bundle = {
        "created_at": created_at(latest),
        "description": latest["body"] or latest["name"],
        "download_url": patches["browser_download_url"],
        "signature_download_url": None,
        "version": latest["tag_name"],
    }

    history = [
        {
            "version": release["tag_name"],
            "created_at": created_at(release),
            "description": release["body"] or release["name"],
        }
        for release in releases
    ]

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "bundle.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n")
    (OUTPUT / "history").write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
