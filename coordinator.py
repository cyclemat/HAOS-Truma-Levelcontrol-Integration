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
        # Timestamp of the last SUCCESSFUL read; None until the first success.
        self.last_success_time: datetime | None = None

    async def _async_update_data(self) -> TrumaReading:
        # Get the BLEDevice HA has actually seen advertising. The LevelControl
        # only advertises now and then; if HA hasn't seen it recently we can't
        # connect, so fail cleanly and let the next cycle retry.
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if ble_device is None:
            # Expected most of the time: the sensor only advertises now and
            # then. Keep it quiet - the last value stays shown.
            _LOGGER.debug("%s not advertising right now, will retry", self.address)
            raise UpdateFailed("sensor not advertising right now")
        try:
            reading = await async_read_measurement(ble_device, name=self.address)
            self.last_success_time = dt_util.utcnow()
            return reading
        except Exception as err:  # noqa: BLE001
            # "device disappeared" between seeing the advert and connecting is
            # also expected for this sensor; log at debug, not error.
            _LOGGER.debug("read attempt failed: %s", err)
            raise UpdateFailed("sensor not reachable this cycle") from err
