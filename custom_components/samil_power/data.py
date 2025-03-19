"""Custom types for Samil Power integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import SamilPowerApiClient
    from .coordinator import SamilPowerDataUpdateCoordinator


type SamilPowerConfigEntry = ConfigEntry[SamilPowerData]


@dataclass
class SamilPowerData:
    """Data for the Samil Power integration."""

    client: SamilPowerApiClient
    coordinator: SamilPowerDataUpdateCoordinator
    integration: Integration
