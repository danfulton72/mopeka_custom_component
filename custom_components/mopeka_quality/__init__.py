"""The Mopeka Quality custom integration."""

# Adapted from Home Assistant Core; modified for HACS and quality filtering.

import logging

from mopeka_iot_ble import MediumType, MopekaIOTBluetoothDeviceData

from homeassistant.components.bluetooth import BluetoothScanningMode
from homeassistant.components.bluetooth.passive_update_processor import PassiveBluetoothProcessorCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_MEDIUM_TYPE, DEFAULT_MEDIUM_TYPE

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


type MopekaConfigEntry = ConfigEntry[PassiveBluetoothProcessorCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: MopekaConfigEntry) -> bool:
    """Set up a Mopeka BLE device from a config entry."""
    address = entry.unique_id
    assert address is not None

    medium_type_str = entry.options.get(
        CONF_MEDIUM_TYPE,
        entry.data.get(CONF_MEDIUM_TYPE, DEFAULT_MEDIUM_TYPE),
    )
    data = MopekaIOTBluetoothDeviceData(MediumType(medium_type_str))
    coordinator = entry.runtime_data = PassiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=address,
        mode=BluetoothScanningMode.PASSIVE,
        update_method=data.update,
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(coordinator.async_start())
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: MopekaConfigEntry) -> bool:
    """Migrate an older Mopeka Quality config entry."""
    if entry.version > 2:
        _LOGGER.error(
            "Cannot migrate Mopeka Quality config entry from unsupported version %s",
            entry.version,
        )
        return False

    if entry.version == 1:
        from .const import CONF_REQUIRED_QUALITY, DEFAULT_REQUIRED_QUALITY

        new_data = {
            **entry.data,
            CONF_REQUIRED_QUALITY: entry.data.get(
                CONF_REQUIRED_QUALITY, DEFAULT_REQUIRED_QUALITY
            ),
        }
        hass.config_entries.async_update_entry(entry, data=new_data, version=2)

    return True


async def update_listener(hass: HomeAssistant, entry: MopekaConfigEntry) -> None:
    """Handle options updates."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: MopekaConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
