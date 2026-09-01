"""Support for Mopeka sensors."""

# Adapted from Home Assistant Core; modified for HACS and quality filtering.

from collections.abc import Mapping
from typing import override

from mopeka_iot_ble import DeviceKey, SensorUpdate

from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info

from . import MopekaConfigEntry
from .const import CONF_REQUIRED_QUALITY, DEFAULT_REQUIRED_QUALITY
from .device import device_key_to_bluetooth_entity_key

SENSOR_DESCRIPTIONS = {
    "battery": SensorEntityDescription(
        key="battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "battery_voltage": SensorEntityDescription(
        key="battery_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    "tank_level": SensorEntityDescription(
        key="tank_level",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "signal_strength": SensorEntityDescription(
        key="signal_strength",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    "reading_quality": SensorEntityDescription(
        key="reading_quality",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "temperature": SensorEntityDescription(
        key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "accelerometer_x": SensorEntityDescription(
        key="accelerometer_x",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    "accelerometer_y": SensorEntityDescription(
        key="accelerometer_y",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
}

QUALITY_SENSOR_KEY = "reading_quality"


def _quality_by_device(sensor_update: SensorUpdate) -> dict[str | None, float]:
    """Return the reported reading quality indexed by device id."""
    result: dict[str | None, float] = {}
    for device_key, sensor_value in sensor_update.entity_values.items():
        if (
            device_key.key == QUALITY_SENSOR_KEY
            and isinstance(sensor_value.native_value, (int, float))
        ):
            result[device_key.device_id] = float(sensor_value.native_value)
    return result


def _value_is_accepted(
    device_key: DeviceKey,
    quality_by_device: Mapping[str | None, float],
    required_quality: int,
) -> bool:
    """Return whether a sensor value passes the configured quality threshold."""
    if device_key.key == QUALITY_SENSOR_KEY:
        return True

    quality = quality_by_device.get(device_key.device_id)
    if quality is None:
        quality = quality_by_device.get(None)
    return quality is not None and quality >= required_quality


def sensor_update_to_bluetooth_data_update(
    sensor_update: SensorUpdate,
    required_quality: int = DEFAULT_REQUIRED_QUALITY,
) -> PassiveBluetoothDataUpdate:
    """Convert a sensor update to a Bluetooth update with quality filtering."""
    quality_by_device = _quality_by_device(sensor_update)

    return PassiveBluetoothDataUpdate(
        devices={
            device_id: sensor_device_info_to_hass_device_info(device_info)
            for device_id, device_info in sensor_update.devices.items()
        },
        entity_descriptions={
            device_key_to_bluetooth_entity_key(device_key): SENSOR_DESCRIPTIONS[
                device_key.key
            ]
            for device_key in sensor_update.entity_descriptions
            if device_key.key in SENSOR_DESCRIPTIONS
        },
        entity_data={
            device_key_to_bluetooth_entity_key(device_key): (
                sensor_values.native_value
                if _value_is_accepted(device_key, quality_by_device, required_quality)
                else None
            )
            for device_key, sensor_values in sensor_update.entity_values.items()
            if device_key.key in SENSOR_DESCRIPTIONS
        },
        entity_names={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.name
            for device_key, sensor_values in sensor_update.entity_values.items()
            if device_key.key in SENSOR_DESCRIPTIONS
        },
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MopekaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Mopeka BLE sensors."""
    coordinator = entry.runtime_data
    required_quality = int(
        entry.options.get(
            CONF_REQUIRED_QUALITY,
            entry.data.get(CONF_REQUIRED_QUALITY, DEFAULT_REQUIRED_QUALITY),
        )
    )
    processor = PassiveBluetoothDataProcessor(
        lambda update: sensor_update_to_bluetooth_data_update(update, required_quality)
    )
    entry.async_on_unload(
        processor.async_add_entities_listener(
            MopekaBluetoothSensorEntity, async_add_entities
        )
    )
    entry.async_on_unload(
        coordinator.async_register_processor(processor, SensorEntityDescription)
    )


class MopekaBluetoothSensorEntity(
    PassiveBluetoothProcessorEntity[
        PassiveBluetoothDataProcessor[float | int | None, SensorUpdate]
    ],
    SensorEntity,
):
    """Representation of a Mopeka sensor."""

    @property
    @override
    def native_value(self) -> int | float | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)
