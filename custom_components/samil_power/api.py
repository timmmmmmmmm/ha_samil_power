"""Samil Power API Client."""

from __future__ import annotations

import asyncio
import logging
import socket
from typing import Any, Dict, List, Tuple

import async_timeout

from .const import LOGGER

# Import the necessary modules from the samil package
from samil.inverter import InverterFinder, KeepAliveInverter, InverterNotFoundError
from samil.inverterutil import connect_inverters


class SamilPowerApiClientError(Exception):
    """Exception to indicate a general API error."""


class SamilPowerApiClientCommunicationError(
    SamilPowerApiClientError,
):
    """Exception to indicate a communication error."""


class SamilPowerApiClientAuthenticationError(
    SamilPowerApiClientError,
):
    """Exception to indicate an authentication error."""


class SamilPowerApiClient:
    """Samil Power API Client."""

    def __init__(
        self,
        interface: str = "",
        inverters: int = 1,
    ) -> None:
        """Initialize the Samil Power API Client."""
        self._interface = interface
        self._inverters_count = int(inverters)  # Ensure this is an integer
        self._inverters = []
        self._model_info = {}
        self._connected = False

    async def async_connect(self) -> None:
        """Connect to the inverters."""
        if self._connected:
            return

        try:
            LOGGER.info(f"Attempting to connect to inverters with interface={self._interface}, count={self._inverters_count}")
            
            # Run the connection in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            self._inverters = await loop.run_in_executor(
                None, self._connect_inverters
            )
            self._connected = True
            
            LOGGER.info(f"Successfully connected to {len(self._inverters)} inverters")
            
            # Get model info for each inverter
            for i, inverter in enumerate(self._inverters):
                self._model_info[i] = await loop.run_in_executor(
                    None, inverter.model
                )
                LOGGER.info(f"Inverter {i} model info: {self._model_info[i].get('model_name', 'Unknown')}, SN: {self._model_info[i].get('serial_number', 'Unknown')}")
                
        except InverterNotFoundError as exception:
            msg = f"No inverters found - {exception}"
            LOGGER.error(msg)
            raise SamilPowerApiClientCommunicationError(msg) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Error connecting to inverters - {exception}"
            LOGGER.error(msg)
            raise SamilPowerApiClientError(msg) from exception

    def _connect_inverters(self):
        """Connect to the inverters (runs in executor)."""
        inverters = []
        try:
            LOGGER.debug(f"Starting inverter connection with interface={self._interface}, count={self._inverters_count}")
            # First try with the specified interface
            finder = InverterFinder(interface_ip=self._interface)
            finder.open()
            try:
                # Find each inverter directly
                for i in range(self._inverters_count):
                    LOGGER.debug(f"Finding inverter {i} with interface {self._interface}")
                    try:
                        sock, addr = finder.find_inverter()
                        LOGGER.info(f"Found inverter at address {addr}")
                        inverter = KeepAliveInverter(sock, addr)
                        inverters.append(inverter)
                    except Exception as e:
                        LOGGER.error(f"Error finding inverter {i}: {str(e)}")
                        if i == 0:  # If we can't find even the first inverter, re-raise
                            raise
            finally:
                finder.close()
        except Exception as e:
            # If there's an error with the specific interface, try with an empty interface (broadcast)
            if self._interface and not inverters:
                # Log that we're falling back to broadcast discovery
                LOGGER.info(f"Failed to connect using interface {self._interface}, trying broadcast discovery")
                # Try again with empty interface for broadcast
                finder = InverterFinder(interface_ip="")
                finder.open()
                try:
                    # Find each inverter directly
                    for i in range(self._inverters_count):
                        LOGGER.debug(f"Finding inverter {i} with broadcast discovery")
                        try:
                            sock, addr = finder.find_inverter()
                            LOGGER.info(f"Found inverter at address {addr} using broadcast discovery")
                            inverter = KeepAliveInverter(sock, addr)
                            inverters.append(inverter)
                        except Exception as e:
                            LOGGER.error(f"Error finding inverter {i} with broadcast: {str(e)}")
                            if i == 0:  # If we can't find even the first inverter, re-raise
                                raise
                finally:
                    finder.close()
            else:
                # Re-raise the original exception if we weren't using a specific interface
                # or if we already have some inverters
                LOGGER.error(f"Error during inverter connection: {str(e)}")
                raise
        
        if not inverters:
            raise InverterNotFoundError("No inverters found")
            
        return inverters

    async def async_get_data(self) -> Dict[int, Dict]:
        """Get data from the inverters."""
        if not self._connected:
            await self.async_connect()

        try:
            # Run the status requests in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Get status for each inverter
            status_data = {}
            for i, inverter in enumerate(self._inverters):
                status = await loop.run_in_executor(None, inverter.status)
                
                # Combine with model info
                combined_data = {
                    "model": self._model_info.get(i, {}),
                    "status": status
                }
                status_data[i] = combined_data
                
            return status_data
            
        except Exception as exception:  # pylint: disable=broad-except
            self._connected = False  # Mark as disconnected on error
            msg = f"Error getting data from inverters - {exception}"
            raise SamilPowerApiClientError(msg) from exception

    async def async_disconnect(self) -> None:
        """Disconnect from the inverters."""
        if not self._connected:
            return
            
        for inverter in self._inverters:
            try:
                inverter.disconnect()
            except Exception:  # pylint: disable=broad-except
                pass
                
        self._inverters = []
        self._connected = False
