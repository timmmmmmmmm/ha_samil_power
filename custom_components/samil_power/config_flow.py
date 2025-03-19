"""Adds config flow for Samil Power."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .api import (
    SamilPowerApiClient,
    SamilPowerApiClientAuthenticationError,
    SamilPowerApiClientCommunicationError,
    SamilPowerApiClientError,
)
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


class SamilPowerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Samil Power."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_connection(
                    interface=user_input.get(CONF_INTERFACE, DEFAULT_INTERFACE),
                    inverters=user_input.get(CONF_INVERTERS, DEFAULT_INVERTERS),
                )
            except SamilPowerApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except SamilPowerApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except SamilPowerApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                # Use a unique ID based on the configuration
                # This allows multiple instances if needed (e.g., for different networks)
                await self.async_set_unique_id(f"samil_power_{user_input.get(CONF_INTERFACE, '')}")
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=f"Samil Power Inverter",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_INTERFACE,
                        default=(user_input or {}).get(CONF_INTERFACE, DEFAULT_INTERFACE),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_INVERTERS,
                        default=(user_input or {}).get(CONF_INVERTERS, DEFAULT_INVERTERS),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=10,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=(user_input or {}).get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=10,
                            max=300,
                            unit_of_measurement="seconds",
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_connection(self, interface: str, inverters: int) -> None:
        """Test connection to the inverters."""
        client = SamilPowerApiClient(
            interface=interface,
            inverters=inverters,
        )
        await client.async_connect()
        await client.async_disconnect()
