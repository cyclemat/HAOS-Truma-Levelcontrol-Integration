"""Truma LevelControl sensors (YAML platform).

Example configuration.yaml:

    sensor:
      - platform: truma_levelcontrol
        address: "18:04:ED:49:1A:78"
        poll_interval: 300        # optional, seconds (default 300)
        name: "Gasflasche"        # optional prefix for entity names

NOTE: use `poll_interval`, NOT `scan_interval`. `scan_interval` is a reserved
HA platform key and must not be redefined here.
"""

from __future__ import annotations

from collections.abc import Callable

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME,
    PERCENTAGE,
    UnitOfMass,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import TrumaCoordinator
from .truma import TrumaReading

CONF_POLL_INTERVAL = "poll_interval"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ADDRESS): cv.string,
        vol.Optional(CONF_NAME, default="Truma LevelControl"): cv.string,
        vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
    }
)


# key, label, unit, device_class, state_class, icon, value getter
_DESCRIPTIONS: list[tuple] = [
    ("fill_level", "Füllstand", PERCENTAGE, None,
     SensorStateClass.MEASUREMENT, "mdi:gauge",
     lambda r: r.percent),
    ("gas_amount", "Gasmenge", UnitOfMass.KILOGRAMS, SensorDeviceClass.WEIGHT,
     SensorStateClass.MEASUREMENT, "mdi:propane-tank",
     lambda r: round(r.kg, 2)),
    ("battery", "Batterie", PERCENTAGE, SensorDeviceClass.BATTERY,
     SensorStateClass.MEASUREMENT, None,
     lambda r: r.battery),
    ("temperature", "Temperatur", UnitOfTemperature.CELSIUS,
     SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None,
     lambda r: r.temperature),
    ("quality", "Messqualität", None, None,
     SensorStateClass.MEASUREMENT, "mdi:signal",
     lambda r: r.quality),
]


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Truma sensors from YAML."""
    address: str = config[CONF_ADDRESS]
    name: str = config[CONF_NAME]
    poll_interval: int = config[CONF_POLL_INTERVAL]

    store = hass.data.setdefault(DOMAIN, {})
    coordinator = store.get(address.upper())
    if coordinator is None:
        coordinator = TrumaCoordinator(hass, address, poll_interval)
        store[address.upper()] = coordinator

    # Do a first refresh, but DO NOT abort setup if it fails: the entities are
    # created regardless and will go from "unavailable" to a value once the
    # device is reachable (it sleeps/advertises only now and then).
    await coordinator.async_refresh()

    entities: list = [
        TrumaSensor(coordinator, address, name, desc) for desc in _DESCRIPTIONS
    ]
    entities.append(TrumaLastSeenSensor(coordinator, address, name))
    async_add_entities(entities)


class TrumaSensor(CoordinatorEntity[TrumaCoordinator], SensorEntity):
    """A single measurement value from the LevelControl."""

    def __init__(
        self,
        coordinator: TrumaCoordinator,
        address: str,
        name_prefix: str,
        desc: tuple,
    ) -> None:
        super().__init__(coordinator)
        key, label, unit, dev_class, state_class, icon, getter = desc
        self._getter: Callable[[TrumaReading], object] = getter

        self._attr_name = f"{name_prefix} {label}"
        self._attr_unique_id = f"{address.upper()}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = dev_class
        self._attr_state_class = state_class
        if icon:
            self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address.upper())},
            name=name_prefix,
            manufacturer="Truma",
            model="LevelControl",
        )

    @property
    def available(self) -> bool:
        # The sensor only advertises every ~18 min, so most poll cycles fail
        # with "device disappeared". Keep the entity available as long as we
        # have EVER got a reading - the last value stays shown until the next
        # successful measurement replaces it. Only truly unavailable before the
        # first-ever success.
        return self.coordinator.data is not None

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self._getter(self.coordinator.data)


class TrumaLastSeenSensor(CoordinatorEntity[TrumaCoordinator], SensorEntity):
    """Timestamp of the last successful measurement.

    Shows up as a relative time ("3 minutes ago") in the UI, so you can always
    tell how fresh the displayed values are. The measurement values stay on
    their last reading between successful polls; this sensor tells you when
    that reading was actually taken.
    """

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-check-outline"

    def __init__(self, coordinator: TrumaCoordinator, address: str, name_prefix: str) -> None:
        super().__init__(coordinator)
        self._attr_name = f"{name_prefix} Zuletzt gelesen"
        self._attr_unique_id = f"{address.upper()}_last_seen"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address.upper())},
            name=name_prefix,
            manufacturer="Truma",
            model="LevelControl",
        )

    @property
    def available(self) -> bool:
        # Available as soon as we have ever read successfully.
        return self.coordinator.last_success_time is not None

    @property
    def native_value(self):
        return self.coordinator.last_success_time
