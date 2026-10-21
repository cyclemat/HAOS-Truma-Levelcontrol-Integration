"""Constants for the Truma LevelControl integration."""

DOMAIN = "truma_levelcontrol"

CONF_ADDRESS = "address"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 300  # seconds (5 minutes)

# --- BLE protocol (reverse-engineered from LevelControl 2.2.1) -------------
_BASE = "-6afe-4cc5-b3ff-3e140baedeb6"
UUID_SERVICE      = "22bfa601" + _BASE
UUID_MEASUREMENT  = "22bfa610" + _BASE   # read / write / notify
UUID_PASSWORD     = "22bfa619" + _BASE   # read -> 5 bytes
UUID_STORE_NV     = "22bfa617" + _BASE   # write trigger

# Store-NV trigger bytes
TRIGGER_INIT = 0x03
TRIGGER_GO = 0x02

# Seconds to wait after triggering before reading the fresh measurement.
MEASURE_WAIT_S = 3.0
