"""Tests for reading-quality filtering."""

from mopeka_iot_ble import DeviceKey, MopekaIOTBluetoothDeviceData

from homeassistant.helpers.service_info.bluetooth import BluetoothServiceInfo

from custom_components.mopeka_quality.device import device_key_to_bluetooth_entity_key
from custom_components.mopeka_quality.sensor import (
    QUALITY_SENSOR_KEY,
    _value_is_accepted,
    sensor_update_to_bluetooth_data_update,
)

PRO_LOW_QUALITY = BluetoothServiceInfo(
    name="",
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    manufacturer_data={89: b"\x08rF\x00@\xe0\xf5\t\xf0\xd8"},
    service_data={},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    source="local",
)

PRO_GOOD_QUALITY = BluetoothServiceInfo(
    name="",
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    manufacturer_data={89: b"\x08pC\xb6\xc3\xe0\xf5\t\xfa\xe3"},
    service_data={},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    source="local",
)


def test_quality_sensor_is_always_accepted() -> None:
    """The quality diagnostic must remain visible even below the threshold."""
    key = DeviceKey(key=QUALITY_SENSOR_KEY, device_id=None)
    assert _value_is_accepted(key, {None: 33.0}, 100)


def test_measurement_at_threshold_is_accepted() -> None:
    """A reading equal to the configured threshold is accepted."""
    key = DeviceKey(key="tank_level", device_id=None)
    assert _value_is_accepted(key, {None: 100.0}, 100)


def test_measurement_below_threshold_is_rejected() -> None:
    """A reading below the configured threshold is rejected."""
    key = DeviceKey(key="tank_level", device_id=None)
    assert not _value_is_accepted(key, {None: 67.0}, 100)


def test_measurement_without_quality_is_rejected() -> None:
    """A reading with no associated quality is rejected safely."""
    key = DeviceKey(key="temperature", device_id="sensor-a")
    assert not _value_is_accepted(key, {}, 0)


def test_device_specific_quality_wins() -> None:
    """Device-specific quality is used when multiple devices are present."""
    key = DeviceKey(key="tank_level", device_id="sensor-a")
    assert _value_is_accepted(key, {None: 0.0, "sensor-a": 67.0}, 50)


def test_converter_rejects_low_quality_values() -> None:
    """The converter makes measurements unknown below the configured threshold."""
    update = MopekaIOTBluetoothDeviceData().update(PRO_LOW_QUALITY)
    assert update is not None

    converted = sensor_update_to_bluetooth_data_update(update, required_quality=100)

    tank_key = device_key_to_bluetooth_entity_key(DeviceKey(key="tank_level", device_id=None))
    temp_key = device_key_to_bluetooth_entity_key(DeviceKey(key="temperature", device_id=None))
    quality_key = device_key_to_bluetooth_entity_key(DeviceKey(key="reading_quality", device_id=None))
    assert converted.entity_data[tank_key] is None
    assert converted.entity_data[temp_key] is None
    assert converted.entity_data[quality_key] == 33


def test_converter_accepts_good_quality_values() -> None:
    """The converter preserves measurements that meet the threshold."""
    update = MopekaIOTBluetoothDeviceData().update(PRO_GOOD_QUALITY)
    assert update is not None

    converted = sensor_update_to_bluetooth_data_update(update, required_quality=100)

    tank_key = device_key_to_bluetooth_entity_key(DeviceKey(key="tank_level", device_id=None))
    temp_key = device_key_to_bluetooth_entity_key(DeviceKey(key="temperature", device_id=None))
    quality_key = device_key_to_bluetooth_entity_key(DeviceKey(key="reading_quality", device_id=None))
    assert converted.entity_data[tank_key] == 341
    assert converted.entity_data[temp_key] == 27
    assert converted.entity_data[quality_key] == 100
