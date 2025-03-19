"""DataUpdateCoordinator for Samil Power integration."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, Dict

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    SamilPowerApiClientAuthenticationError,
    SamilPowerApiClientError,
)
from .const import LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from .data import SamilPowerConfigEntry


class SamilPowerDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Samil Power inverters."""

    config_entry: SamilPowerConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name="Samil Power",
            update_interval=update_interval,
        )
        self.inverter_data: Dict[int, Dict] = {}

    async def _async_update_data(self) -> Dict[int, Dict]:
        """Update data via library."""
        try:
            self.inverter_data = await self.config_entry.runtime_data.client.async_get_data()
            LOGGER.debug("Updated inverter data: %s", self.inverter_data)
            return self.inverter_data
        except SamilPowerApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except SamilPowerApiClientError as exception:
            raise UpdateFailed(exception) from exception
