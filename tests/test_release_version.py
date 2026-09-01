"""Tests for automated release version handling."""

import json
from pathlib import Path

import pytest

from scripts.release_version import (
    next_patch_version,
    normalize_version,
    set_manifest_version,
)


@pytest.mark.parametrize(
    ("current", "expected"),
    [
        ("0.0.0", "0.0.1"),
        ("v1.2.3", "1.2.4"),
        ("9.99.999", "9.99.1000"),
    ],
)
def test_next_patch_version(current: str, expected: str) -> None:
    """Test patch version increments."""
    assert next_patch_version(current) == expected


@pytest.mark.parametrize("invalid", ["", "1.2", "1.2.3.4", "release-1.2.3"])
def test_normalize_version_rejects_invalid_tags(invalid: str) -> None:
    """Only strict semantic x.y.z release tags are supported."""
    with pytest.raises(ValueError):
        normalize_version(invalid)


def test_set_manifest_version(tmp_path: Path) -> None:
    """Test manifest synchronization without changing its domain."""
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        '{"domain":"mopeka_quality","version":"0.0.0"}', encoding="utf-8"
    )

    set_manifest_version(manifest, "2.4.6")

    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["domain"] == "mopeka_quality"
    assert data["version"] == "2.4.6"
