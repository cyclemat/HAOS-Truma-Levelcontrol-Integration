"""Polling coordinator for the Truma LevelControl."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .truma import TrumaReading, async_read_measurement

_LOGGER = logging.getLogger(__name__)


class TrumaCoordinator(DataUpdateCoordinator[TrumaReading]):
    """Connects to the sensor on a schedule and keeps the latest reading."""

    def __init__(
        self, hass: HomeAssistant, address: str, scan_interval: int
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {address}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.address = address.upper()

    async def _async_update_data(self) -> TrumaReading:
        # Prefer the BLEDevice that HA already knows about (works with the
        # local adapter and with remote ESPHome Bluetooth proxies).
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        target = ble_device or self.address
        if ble_device is None:
            _LOGGER.debug(
                "device %s not seen by HA bluetooth yet, trying by address",
                self.address,
            )
        try:
            return await async_read_measurement(target)
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"error reading Truma LevelControl: {err}") from err
