"""Sensor platform for Samil Power integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

from .const import DOMAIN, LOGGER
from .entity import SamilPowerEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SamilPowerDataUpdateCoordinator
    from .data import SamilPowerConfigEntry


@dataclass
class SamilPowerSensorEntityDescription(SensorEntityDescription):
    """Class describing Samil Power sensor entities."""

    value_fn: Optional[callable] = None


SENSOR_DESCRIPTIONS = (
    # Power sensors
    SamilPowerSensorEntityDescription(
        key="output_power",
        name="Output Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
        value_fn=lambda data: data.get("status", {}).get("output_power"),
    ),
    SamilPowerSensorEntityDescription(
        key="pv1_input_power",
        name="PV1 Input Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
        value_fn=lambda data: data.get("status", {}).get("pv1_input_power"),
    ),
    SamilPowerSensorEntityDescription(
        key="pv2_input_power",
        name="PV2 Input Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
        value_fn=lambda data: data.get("status", {}).get("pv2_input_power"),
    ),
    
    # Energy sensors
    SamilPowerSensorEntityDescription(
        key="energy_today",
        name="Energy Today",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        value_fn=lambda data: data.get("status", {}).get("energy_today"),
    ),
    SamilPowerSensorEntityDescription(
        key="energy_total",
        name="Energy Total",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        value_fn=lambda data: data.get("status", {}).get("energy_total"),
    ),
    
    # Voltage sensors
    SamilPowerSensorEntityDescription(
        key="pv1_voltage",
        name="PV1 Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        value_fn=lambda data: data.get("status", {}).get("pv1_voltage"),
    ),
    SamilPowerSensorEntityDescription(
        key="pv2_voltage",
        name="PV2 Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        value_fn=lambda data: data.get("status", {}).get("pv2_voltage"),
    ),
    SamilPowerSensorEntityDescription(
        key="grid_voltage",
        name="Grid Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
        value_fn=lambda data: data.get("status", {}).get("grid_voltage"),
    ),
    
    # Current sensors
    SamilPowerSensorEntityDescription(
        key="pv1_current",
        name="PV1 Current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        value_fn=lambda data: data.get("status", {}).get("pv1_current"),
    ),
    SamilPowerSensorEntityDescription(
        key="pv2_current",
        name="PV2 Current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        value_fn=lambda data: data.get("status", {}).get("pv2_current"),
    ),
    SamilPowerSensorEntityDescription(
        key="grid_current",
        name="Grid Current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
        value_fn=lambda data: data.get("status", {}).get("grid_current"),
    ),
    
    # Frequency sensor
    SamilPowerSensorEntityDescription(
        key="grid_frequency",
        name="Grid Frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
        value_fn=lambda data: data.get("status", {}).get("grid_frequency"),
    ),
    
    # Temperature sensors
    SamilPowerSensorEntityDescription(
        key="internal_temperature",
        name="Internal Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        value_fn=lambda data: data.get("status", {}).get("internal_temperature"),
    ),
    SamilPowerSensorEntityDescription(
        key="heatsink_temperature",
        name="Heatsink Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        value_fn=lambda data: data.get("status", {}).get("heatsink_temperature"),
    ),
    
    # Operation mode and time
    SamilPowerSensorEntityDescription(
        key="operation_mode",
        name="Operation Mode",
        icon="mdi:state-machine",
        value_fn=lambda data: data.get("status", {}).get("operation_mode"),
    ),
    SamilPowerSensorEntityDescription(
        key="total_operation_time",
        name="Total Operation Time",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
        value_fn=lambda data: data.get("status", {}).get("total_operation_time"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SamilPowerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Samil Power sensor platform."""
    coordinator = entry.runtime_data.coordinator
    
    # Wait for the coordinator to get data at least once
    await coordinator.async_config_entry_first_refresh()
    
    entities = []
    
    # Create entities for each inverter
    for inverter_index in coordinator.data:
        LOGGER.debug(
            "Setting up sensors for inverter %s", inverter_index
        )
        
        # Add all sensor types for this inverter
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                SamilPowerSensor(
                    coordinator=coordinator,
                    entity_description=description,
                    inverter_index=inverter_index,
                )
            )
    
    async_add_entities(entities)


class SamilPowerSensor(SamilPowerEntity, SensorEntity):
    """Samil Power Sensor class."""

    entity_description: SamilPowerSensorEntityDescription

    def __init__(
        self,
        coordinator: SamilPowerDataUpdateCoordinator,
        entity_description: SamilPowerSensorEntityDescription,
        inverter_index: int,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, inverter_index, entity_description)
        self.entity_description = entity_description

    @property
    def native_value(self) -> Any:
        """Return the native value of the sensor."""
        if self.coordinator.data and self.entity_description.value_fn:
            inverter_data = self.get_inverter_data()
            return self.entity_description.value_fn(inverter_data)
        return None
