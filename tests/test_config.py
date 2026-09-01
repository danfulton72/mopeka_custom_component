"""Tests for Mopeka configuration and migration."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import voluptuous as vol

from custom_components.mopeka import async_migrate_entry
from custom_components.mopeka.config_flow import async_generate_schema
from custom_components.mopeka.const import (
    CONF_MEDIUM_TYPE,
    CONF_REQUIRED_QUALITY,
    DEFAULT_MEDIUM_TYPE,
    DEFAULT_REQUIRED_QUALITY,
)


def test_schema_defaults() -> None:
    """Test the configuration schema defaults."""
    validated = async_generate_schema()({})
    assert validated[CONF_MEDIUM_TYPE] == DEFAULT_MEDIUM_TYPE
    assert validated[CONF_REQUIRED_QUALITY] == DEFAULT_REQUIRED_QUALITY


def test_schema_accepts_quality_bounds() -> None:
    """Test valid boundary values for required quality."""
    schema = async_generate_schema()
    assert schema({CONF_REQUIRED_QUALITY: 0})[CONF_REQUIRED_QUALITY] == 0
    assert schema({CONF_REQUIRED_QUALITY: 100})[CONF_REQUIRED_QUALITY] == 100


def test_schema_rejects_out_of_range_quality() -> None:
    """Test invalid required quality values."""
    schema = async_generate_schema()
    for invalid in (-1, 101):
        try:
            schema({CONF_REQUIRED_QUALITY: invalid})
        except vol.Invalid:
            pass
        else:
            raise AssertionError(f"{invalid} should be rejected")


async def test_migrate_entry_adds_required_quality() -> None:
    """Test migration from the Core version-one config entry."""
    hass = MagicMock()
    entry = SimpleNamespace(version=1, data={CONF_MEDIUM_TYPE: DEFAULT_MEDIUM_TYPE})

    assert await async_migrate_entry(hass, entry)

    hass.config_entries.async_update_entry.assert_called_once_with(
        entry,
        data={
            CONF_MEDIUM_TYPE: DEFAULT_MEDIUM_TYPE,
            CONF_REQUIRED_QUALITY: DEFAULT_REQUIRED_QUALITY,
        },
        version=2,
    )


async def test_migrate_entry_rejects_newer_version() -> None:
    """Test migration fails safely for unsupported future versions."""
    hass = MagicMock()
    entry = SimpleNamespace(version=3, data={})

    assert not await async_migrate_entry(hass, entry)
    hass.config_entries.async_update_entry.assert_not_called()
