"""Button to manually trigger a Truma LevelControl measurement.

Example configuration.yaml (same address as the sensor):

    button:
      - platform: truma_levelcontrol
        address: "18:04:ED:49:1A:78"
        name: "Gasflasche"
"""

from __future__ import annotations

import voluptuous as vol

from homeassistant.components.button import PLATFORM_SCHEMA, ButtonEntity
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import TrumaCoordinator

CONF_POLL_INTERVAL = "poll_interval"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ADDRESS): cv.string,
        vol.Optional(CONF_NAME, default="Truma LevelControl"): cv.string,
        vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the manual-measure button.

    Reuses the shared coordinator for this address if the sensor platform
    already created one, so the button and the sensors stay in sync.
    """
    address: str = config[CONF_ADDRESS]
    name: str = config[CONF_NAME]
    poll_interval: int = config[CONF_POLL_INTERVAL]

    store = hass.data.setdefault(DOMAIN, {})
    coordinator = store.get(address.upper())
    if coordinator is None:
        coordinator = TrumaCoordinator(hass, address, poll_interval)
        store[address.upper()] = coordinator

    async_add_entities([TrumaMeasureButton(coordinator, address, name)])


class TrumaMeasureButton(ButtonEntity):
    """Press to take a fresh measurement now."""

    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: TrumaCoordinator, address: str, name_prefix: str) -> None:
        self._coordinator = coordinator
        self._attr_name = f"{name_prefix} Messung auslösen"
        self._attr_unique_id = f"{address.upper()}_measure_now"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address.upper())},
            name=name_prefix,
            manufacturer="Truma",
            model="LevelControl",
        )

    async def async_press(self) -> None:
        """Trigger a fresh measurement; sensors update from the result."""
        await self._coordinator.async_request_refresh()
