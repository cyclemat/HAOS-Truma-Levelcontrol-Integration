[![Truma LevelControl for Home Assistant](https://raw.githubusercontent.com/cyclemat/Home-Assistant-Truma-LevelControl/main/assets/banner.png)](https://raw.githubusercontent.com/cyclemat/Home-Assistant-Truma-LevelControl/main/assets/banner.png)

# ⛽ Truma LevelControl for Home Assistant

### Read your gas bottle level over Bluetooth – local, private & app-free

![Platform: Home Assistant](https://img.shields.io/badge/Platform-Home%20Assistant-blue.svg)
![Type: Integration](https://img.shields.io/badge/Type-Custom%20Integration-blue.svg)
![Connection: Bluetooth LE](https://img.shields.io/badge/Connection-Bluetooth%20LE-blueviolet.svg)
![Config: UI Discovery](https://img.shields.io/badge/Setup-Auto%20Discovery-yellow)
![Status: Active Development](https://img.shields.io/badge/Status-Active%20Development-green.svg)

---

## 🚀 About This Integration

This custom integration brings your **Truma LevelControl** gas-bottle sensor
directly into **Home Assistant** – over Bluetooth, with no cloud and without the
Truma phone app.

The BLE protocol was reverse-engineered from the official app and verified
against real readings. The integration connects to the sensor, triggers a fresh
measurement and exposes everything as native sensors.

> **Know how much gas is left – right on your dashboard, fully local.**

It provides:

- 🔹 Fill level (%) and gas amount (kg)
- 🔹 Battery and temperature
- 🔹 Measurement quality
- 🔹 A "last successfully read" timestamp
- 🔹 A button to trigger a measurement on demand

---

## 🎯 Why This Exists

The Truma LevelControl only talks to its own phone app. If you live in a camper
or caravan running Home Assistant, you want that gas level **in HA** – next to
your battery, water and temperature sensors.

Benefits:

- 🏠 Everything runs **locally** – no Truma cloud, no app
- 🔐 Full control over your own data
- ♻️ Values stay shown between readings (the sensor only advertises now and then)
- ⚡ Integrated into your existing HA ecosystem

---

## 📊 Sensors

| Entity | Description | Unit |
|--------|-------------|------|
| Füllstand | Gas fill level | % |
| Gasmenge | Gas amount | kg |
| Batterie | Sensor battery | % |
| Temperatur | Sensor temperature | °C |
| Messqualität | Measurement quality | 0–3 |
| Zuletzt gelesen | Timestamp of last successful read | — |

Plus a **button** entity to trigger a fresh measurement at any time.

---

## 🧩 Installation

### Option A — HACS (recommended)

1. In HACS, add this repository as a **custom repository** (type: *Integration*).
2. Install **Truma LevelControl**.
3. Restart Home Assistant.

### Option B — Manual

1. Copy the `custom_components/truma_levelcontrol` folder into your
   `/config/custom_components/` directory.
2. Restart Home Assistant.

### Setup

Once the sensor is in range, Home Assistant **auto-discovers** it and shows a
notification under **Settings → Devices & Services**. Click it, confirm, done.

If it isn't discovered automatically, add it manually:
**Settings → Devices & Services → Add Integration → "Truma LevelControl"**,
then enter the sensor's Bluetooth MAC address.

The measurement interval is configurable per device under **Configure**.

---

## 📡 Bluetooth Range & Reliability

The sensor advertises only every few minutes and allows a single BLE connection
at a time. For a reliable setup:

- Keep a Bluetooth adapter **in range** of the bottle.
- Use a solid BLE adapter – cheap combo sticks (e.g. Barrot-based) often fail to
  connect even with a strong signal. An **RTL8761B** USB adapter or an **ESP32
  Bluetooth proxy** near the bottle works best.
- Close the phone app while HA is polling – only one connection is allowed.

---

## ⚠️ Disclaimer

This project is a **community-driven, private hobby project**.

- I am **not affiliated with Truma** or any related company.
- "Truma" and "LevelControl" are trademarks of their respective owners.
- This integration only provides **interoperability with your own device**.
- Use at your own risk.

---

## ❤️ Support & Donations

This integration is **free to use**.

If it helps you and you'd like to support further development, you're welcome to
leave a small donation — **completely optional**:

👉 **Donate via PayPal:** [http://paypal.me/cyclemat](http://paypal.me/cyclemat)

No pressure, no ads, no paywalls.
Just open-source and passion ❤️

---

## 🛠️ Feedback & Contributions

- Issues and suggestions are welcome
- Feel free to open pull requests
- Tested on additional LevelControl firmware? Let me know!

---

[![Truma LevelControl](https://raw.githubusercontent.com/cyclemat/Home-Assistant-Truma-LevelControl/main/assets/logo.png)](https://raw.githubusercontent.com/cyclemat/Home-Assistant-Truma-LevelControl/main/assets/logo.png)

**Your gas. Your data. Your dashboard.**
