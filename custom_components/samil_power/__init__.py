"""
Custom integration to integrate Samil Power inverters with Home Assistant.

For more details about this integration, please refer to
https://github.com/timmmmmmmmm/samil_power
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.loader import async_get_loaded_integration

from .api import SamilPowerApiClient
from .const import (
    CONF_INTERFACE,
    CONF_INVERTERS,
    CONF_SCAN_INTERVAL,
    DEFAULT_INTERFACE,
    DEFAULT_INVERTERS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)
from .coordinator import SamilPowerDataUpdateCoordinator
from .data import SamilPowerData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SamilPowerConfigEntry

# Only using the sensor platform for now
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: SamilPowerConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    LOGGER.debug("Setting up Samil Power integration")
    
    # Get configuration from entry
    interface = entry.data.get(CONF_INTERFACE, DEFAULT_INTERFACE)
    inverters = entry.data.get(CONF_INVERTERS, DEFAULT_INVERTERS)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    
    # Create coordinator with appropriate update interval
    coordinator = SamilPowerDataUpdateCoordinator(
        hass=hass,
        update_interval=timedelta(seconds=scan_interval),
    )
    
    # Create API client
    client = SamilPowerApiClient(
        interface=interface,
        inverters=inverters,
    )
    
    # Store runtime data
    entry.runtime_data = SamilPowerData(
        client=client,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )
    
    # Connect to the inverters
    try:
        await client.async_connect()
    except Exception as ex:
        LOGGER.error("Failed to connect to inverters: %s", ex)
        return False

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    # Add a callback to disconnect when unloaded
    async def async_disconnect_client():
        """Disconnect from the inverters when unloaded."""
        await client.async_disconnect()
        
    entry.async_on_unload(async_disconnect_client)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: SamilPowerConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: SamilPowerConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
