#!/usr/bin/env python3
"""Compute release versions and keep manifest.json synchronized."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def normalize_version(tag: str) -> tuple[int, int, int]:
    """Parse a strict x.y.z release tag."""
    match = SEMVER_RE.fullmatch(tag.strip())
    if match is None:
        raise ValueError(f"Unsupported release tag: {tag!r}")
    return tuple(int(part) for part in match.groups())


def next_patch_version(tag: str) -> str:
    """Increment the patch number from a GitHub release tag."""
    major, minor, patch = normalize_version(tag)
    return f"{major}.{minor}.{patch + 1}"


def set_manifest_version(manifest_path: Path, version: str) -> None:
    """Write a release version into the integration manifest."""
    normalize_version(version)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["version"] = version.removeprefix("v")
    manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest-tag", required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("custom_components/mopeka_quality/manifest.json"),
    )
    args = parser.parse_args()

    version = next_patch_version(args.latest_tag)
    set_manifest_version(args.manifest, version)
    print(version)


if __name__ == "__main__":
    main()
