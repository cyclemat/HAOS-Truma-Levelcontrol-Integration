"""Constants for the Truma LevelControl integration."""

DOMAIN = "truma_levelcontrol"

CONF_POLL_INTERVAL = "poll_interval"
DEFAULT_POLL_INTERVAL = 600  # seconds (10 minutes)

# Advertising: older sensors send manufacturer ID 0x5000. Newer firmware sends no
# fixed manufacturer ID (the first bytes change with every packet) but advertises
# the 16-bit service 0x0A00, the local name is "T" + one byte + the bottle type set
# in the Truma app (e.g. "Alugas 11kg"). HA discovery matches on all of them; see
# manifest.json "bluetooth".
MANUFACTURER_ID = 0x5000
ADV_SERVICE_UUID = "00000a00-0000-1000-8000-00805f9b34fb"

# --- BLE protocol (reverse-engineered from LevelControl 2.2.1) -------------
_BASE = "-6afe-4cc5-b3ff-3e140baedeb6"
UUID_SERVICE      = "22bfa601" + _BASE
UUID_MEASUREMENT  = "22bfa610" + _BASE   # read / write / notify
UUID_PASSWORD     = "22bfa619" + _BASE   # read -> 5 bytes
UUID_STORE_NV     = "22bfa617" + _BASE   # write trigger

TRIGGER_INIT = 0x03
TRIGGER_GO = 0x02

MEASURE_WAIT_S = 3.0
