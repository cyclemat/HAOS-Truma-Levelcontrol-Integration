**** Testing Version *****
PLease give feedback


Truma LevelControl — BLE Readout
Read your Truma LevelControl gas-bottle sensor over
Bluetooth Low Energy, without the official app. Includes a standalone Python
reader and a Home Assistant integration.
The BLE protocol was reverse-engineered from the official Android app
(LevelControl 2.2.1) and verified against real readings.
> **Disclaimer.** This is an unofficial, independent project, not affiliated
> with or endorsed by Truma. Use it with your own device, at your own risk.
> "Truma" and "LevelControl" are trademarks of their respective owner.
---
What it does
Connects to the sensor, forces a fresh measurement, and reads:
Value	Unit	Notes
Fill level	%	0–100
Gas amount	kg	rounded to 100 g steps by the device
Battery	%	sensor battery
Temperature	°C	measured at the sensor
Quality	0–3	measurement confidence (3 = good)
Accuracy was confirmed against the official app: temperature and battery match
exactly, fill level and gas amount to within one 100 g step (the device reports
grams in 100 g resolution on this characteristic).
---
The protocol
All custom characteristics live under the Truma service
`22BFA601-6AFE-4CC5-B3FF-3E140BAEDEB6`.
1. Read the password from characteristic `22BFA619-…` → 5 bytes.
2. Derive the RC4 key by XOR-ing those 5 bytes with the ASCII string
`"TRUMA"` (`0x54 0x52 0x55 0x4D 0x41`):
```
key[i] = password[i] XOR "TRUMA"[i]
```
3. Trigger a fresh measurement by writing single bytes to the Store-NV
characteristic `22BFA617-…` (write without response):
```
write 0x03   (initialize)
write 0x02   (trigger)
wait ~3 s    (ultrasonic measurement)
```
A plain read without this step returns a stale cached value.
4. Read and decrypt the measurement from `22BFA610-…`, then RC4-decrypt the
bytes with the key from step 2.
5. Parse the decrypted little-endian payload:
```
byte[0]      fill level in %
byte[1..2]   grams / 100   (uint16 LE, multiply by 100)
byte[3]      battery in %
byte[4]      temperature in °C
byte[6] >> 6 measurement quality (0–3)
```
Standard GATT Device Information service `180A` also exposes the serial number
(`2A25`) and firmware version (`2A26`) in clear text.
---
Repository contents
```
truma_read_final.py        Standalone reader (scan, pick, trigger, decode)
truma_pick_and_read.py      Earlier interactive reader (device picker)
truma_dump_all.py           Diagnostic: dumps every characteristic
scan_all.py                 Diagnostic: lists all nearby BLE devices
custom_components/
  truma_levelcontrol/       Home Assistant integration
```
---
Standalone Python reader
Requires Python 3.12 (newer versions may lack prebuilt `bleak`/`winrt` wheels
on Windows) and the `bleak` library.
```bash
pip install bleak
```
First run scans and lets you pick the device; the MAC is saved to
`truma_device.txt` and reused afterwards.
```bash
python truma_read_final.py          # read (scans + picks if none saved)
python truma_read_final.py --pick   # choose a different device
```
Example output:
```
  Fill level : 38 %
  Gas amount : 4.20 kg  (4200 g)
  Battery    : 100 %
  Temperature: 13 °C
  Quality    : 3/3
```
Notes
Close the phone app first — the sensor allows only one BLE connection.
On Windows the device may need to be paired in Bluetooth settings before a
connection succeeds.
The 3 s measurement wait is a safe default; running twice back-to-back
guarantees a fresh value.
---
Home Assistant integration
A YAML-configured custom integration that uses Home Assistant's own Bluetooth
stack — so it works with the local adapter and with ESPHome Bluetooth
proxies without any change.
Install
Copy `custom_components/truma_levelcontrol/` into your HA `/config/custom_components/`
directory (via the Samba share, Studio Code Server, or File editor add-on).
Add to `configuration.yaml`:
```yaml
   sensor:
     - platform: truma_levelcontrol
       address: "18:04:ED:49:1A:78"   # your sensor's MAC
       name: "Gas bottle"
       scan_interval: 300             # seconds (default 300)
   ```
Restart Home Assistant.
Five sensors appear (fill level, gas amount, battery, temperature, quality).
Tuning
`scan_interval` controls how often a measurement is taken. 300 s (5 min) is a
sensible default; lower values wake the sensor more often and use more battery
for little benefit, since the gas level changes slowly.
The post-trigger wait is `MEASURE_WAIT_S` in `const.py` — increase it if
readings look stale.
Range / ESPHome proxy
BLE does not travel well through the metal of a vehicle. If the HA device is
more than a few metres from the bottle, add an ESP32 running ESPHome as an
active (connectable) Bluetooth proxy near the gas locker. The integration
needs no changes — all Truma logic stays in HA; the ESP32 only relays the radio.
---
How it was reverse-engineered
The app's APK (Kotlin, lightly obfuscated) was unpacked and its DEX bytecode
disassembled to recover:
the service and characteristic UUIDs (`TrulcBleConstants`),
the RC4 key derivation (`PasswordUtils`, XOR with `"TRUMA"`),
the measurement trigger sequence (`triggerMeasurement` / `initializeMeasurement`
writing `0x02` / `0x03` to Store-NV),
the measurement byte layout (`MeasurementData.decrypt`).
The byte layout was then confirmed empirically by comparing decoded readings
against the values shown in the official app at known fill levels.
