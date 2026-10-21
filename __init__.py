"""The Truma LevelControl integration (YAML-configured)."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up via configuration.yaml (the sensor platform does the work)."""
    hass.data.setdefault(DOMAIN, {})
    return True
