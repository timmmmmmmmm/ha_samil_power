"""SamilPowerEntity class."""

from __future__ import annotations

from typing import Any, Dict

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import SamilPowerDataUpdateCoordinator


class SamilPowerEntity(CoordinatorEntity[SamilPowerDataUpdateCoordinator]):
    """SamilPowerEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self, 
        coordinator: SamilPowerDataUpdateCoordinator,
        inverter_index: int,
        entity_description=None,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.inverter_index = inverter_index
        self._entity_key = entity_description.key if entity_description else None
        
        # Get model info for this inverter
        model_info = self.get_inverter_data().get("model", {})
        serial_number = model_info.get("serial_number", f"unknown_{inverter_index}")
        model_name = model_info.get("model_name", "Samil Power Inverter")
        manufacturer = model_info.get("manufacturer", "Samil Power")
        
        # Create a unique ID based on the serial number and entity key
        if self._entity_key:
            self._attr_unique_id = f"{serial_number}_{self._entity_key}"
            # Prepend "samil_" to the entity_id to make it more specific
            self._attr_entity_id = f"samil_{self._entity_key}"
        
        # Set up device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial_number)},
            name=f"Samil Power Inverter {serial_number}",
            manufacturer=manufacturer,
            model=model_name,
            sw_version=model_info.get("firmware_version", "Unknown"),
        )

    def get_inverter_data(self) -> Dict[str, Any]:
        """Get the current data for this inverter."""
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get(self.inverter_index, {})
