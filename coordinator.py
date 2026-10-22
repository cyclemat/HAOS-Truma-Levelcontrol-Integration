"""Polling coordinator for the Truma LevelControl."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .truma import TrumaReading, async_read_measurement

_LOGGER = logging.getLogger(__name__)


class TrumaCoordinator(DataUpdateCoordinator[TrumaReading]):
    """Connects to the sensor on a schedule and keeps the latest reading."""

    def __init__(
        self, hass: HomeAssistant, address: str, poll_interval: int
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {address}",
            update_interval=timedelta(seconds=poll_interval),
        )
        self.address = address.upper()
        self.last_success_time: datetime | None = None

    async def _async_update_data(self) -> TrumaReading:
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if ble_device is None:
            _LOGGER.debug("%s not advertising right now, will retry", self.address)
            raise UpdateFailed("sensor not advertising right now")
        try:
            reading = await async_read_measurement(ble_device, name=self.address)
            self.last_success_time = dt_util.utcnow()
            return reading
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("read attempt failed: %s", err)
            raise UpdateFailed("sensor not reachable this cycle") from err
