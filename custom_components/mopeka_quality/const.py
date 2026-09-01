"""Constants for the Mopeka Quality integration."""

# Adapted from Home Assistant Core; modified for HACS and quality filtering.

from typing import Final

from mopeka_iot_ble import MediumType

DOMAIN = "mopeka_quality"

CONF_MEDIUM_TYPE: Final = "medium_type"
CONF_REQUIRED_QUALITY: Final = "required_quality"

DEFAULT_MEDIUM_TYPE = MediumType.PROPANE.value
DEFAULT_REQUIRED_QUALITY: Final = 100

MIN_REQUIRED_QUALITY: Final = 0
MAX_REQUIRED_QUALITY: Final = 100
