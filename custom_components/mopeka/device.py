"""Support for Mopeka devices."""

# Adapted from Home Assistant Core; modified for HACS and quality filtering.

from mopeka_iot_ble import DeviceKey

from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothEntityKey,
)


def device_key_to_bluetooth_entity_key(
    device_key: DeviceKey,
) -> PassiveBluetoothEntityKey:
    """Convert a device key to an entity key."""
    return PassiveBluetoothEntityKey(device_key.key, device_key.device_id)
