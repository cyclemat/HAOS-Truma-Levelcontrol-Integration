"""The Truma LevelControl integration (YAML-configured)."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

# Platforms are configured individually under their own YAML keys
# (sensor:, button:). Nothing to forward here; we just ensure the
# shared data store exists.


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the shared data store for the integration."""
    hass.data.setdefault(DOMAIN, {})
    return True
