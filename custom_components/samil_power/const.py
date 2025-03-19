"""Constants for Samil Power integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "samil_power"
ATTRIBUTION = "Data provided by Samil Power inverter"

# Configuration
CONF_INTERFACE = "interface"
CONF_INVERTERS = "inverters"
CONF_SCAN_INTERVAL = "scan_interval"

# Default values
DEFAULT_INTERFACE = ""
DEFAULT_INVERTERS = 1
DEFAULT_SCAN_INTERVAL = 30  # seconds
