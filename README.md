<h1 align="center">📡 Embedded IoT Telemetry System: STM32L475, Wi-Fi & Node-RED</h1>

<p align="center">
  <strong>Local Industrial Networks & IoT Systems (3GE) — ENIT, École Nationale d'Ingénieurs de Tunis</strong><br/>
  <em>Multi-Sensor Edge Acquisition, Custom Lightweight MQTT Stack, Node-RED Dashboard & Time-Series SQLite Logging</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/MCU-STM32L475VG%20(ARM%20Cortex--M4)-002B49?style=for-the-badge&logo=stmicroelectronics&logoColor=white"/>
  <img src="https://img.shields.io/badge/Board-B--L475E--IOT01A-03234B?style=for-the-badge&logo=stmicroelectronics&logoColor=white"/>
  <img src="https://img.shields.io/badge/Connectivity-Wi--Fi%20ISM43362-FF6600?style=for-the-badge&logo=wi-fi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Protocol-MQTT%20v3.1.1-660066?style=for-the-badge&logo=eclipsemosquitto&logoColor=white"/>
  <img src="https://img.shields.io/badge/Dashboard-Node--RED-8F0000?style=for-the-badge&logo=nodered&logoColor=white"/>
  <img src="https://img.shields.io/badge/Database-SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/Analytics-Python%20%7C%20Pandas%20%7C%20Matplotlib-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Hardware & Sensors Inventory](#-hardware--sensors-inventory)
- [Firmware Architecture](#-firmware-architecture)
  - [Dual-Rate Scheduling](#dual-rate-scheduling)
  - [Wi-Fi Subsystem (Inventek ISM43362)](#wi-fi-subsystem-inventek-ism43362)
  - [Lightweight Embedded MQTT Client](#lightweight-embedded-mqtt-client)
- [Node-RED Dashboard & Pipeline](#-node-red-dashboard--pipeline)
- [Data Storage & Relational Schema](#-data-storage--relational-schema)
- [Statistical Analysis & Validation](#-statistical-analysis--validation)
- [Repository Structure](#-repository-structure)
- [Quickstart Guide](#-quickstart-guide)
  - [1. Mosquitto Broker Setup](#1-mosquitto-broker-setup)
  - [2. Node-RED Setup](#2-node-red-setup)
  - [3. Firmware Build & Flash](#3-firmware-build--flash)
  - [4. Software Simulation (Hardware-Free Testing)](#4-software-simulation-hardware-free-testing)
- [Author & Academic Attribution](#-author--academic-attribution)
- [License](#-license)

---

## 🎯 Overview

This project delivers a **complete end-to-end industrial IoT telemetry solution** running on the **STMicroelectronics B-L475E-IOT01A Discovery kit** (ARM Cortex-M4 with FPU). 

The system reads environmental parameters (Temperature, Relative Humidity, Barometric Pressure) and 9-DoF inertial dynamics (3D Accelerometer, 3D Gyroscope, 3D Magnetometer). The telemetry data is formatted into binary MQTT packets, transmitted over **Wi-Fi** using the onboard **Inventek ISM43362** module, ingested by a local **Mosquitto broker**, processed through a modular **Node-RED** flow, displayed on a responsive **live dashboard**, and persistently archived into an **SQLite time-series relational database**.

### Key Engineering Highlights

| Feature | Technical Implementation |
|---|---|
| ⚡ **Microcontroller** | STM32L475VGT6 (80 MHz ARM Cortex-M4, 1 MB Flash, 128 KB SRAM) |
| 🌡️ **Environmental Sensors** | HTS221 (Temp/Hum) and LPS22HB (Barometer) polled via I2C2 |
| 🏃 **Inertial Dynamics** | LSM6DSL 3D Accel/Gyro polled at 20 Hz (50 ms) for rapid shake detection ($|a|^2 > 2.25\,g^2$) |
| 📶 **Wi-Fi Stack** | Inventek ISM43362-M3G-L44 eS-WiFi module driven via SPI3 with AT-command state machine |
| 📦 **Custom MQTT Engine** | Minimal zero-overhead embedded MQTT v3.1.1 packet serializer (Connect / Publish) |
| 📊 **Supervision & UI** | Node-RED real-time dashboard featuring interactive gauges, trend charts, and historical logs |
| 💾 **Relational Storage** | Automated SQLite database insertion with SQL UPSERT/aggregation capabilities |
| 📈 **Data Analytics** | Python toolset (Pandas, Matplotlib) for exploratory telemetry analysis and multi-axis visualization |

---

## 🏗 System Architecture

The following diagram illustrates the data flow from physical silicon to supervision dashboard and analytics:

`
┌────────────────────────────────────────────────────────────────────────┐
│                   EDGE NODE: STM32L475 DISCOVERY                       │
│                                                                        │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐          │
│   │    HTS221    │     │   LPS22HB    │     │   LSM6DSL    │          │
│   │ Temp & Humid │     │ Baro Pressure│     │ Accel & Gyro │          │
│   └──────┬───────┘     └──────┬───────┘     └──────┬───────┘          │
│          │ I2C2               │ I2C2               │ SPI3             │
│   ┌──────▼────────────────────▼────────────────────▼───────┐          │
│   │                STM32L475 HAL Firmware                  │          │
│   │  - 50 ms loop: 3D Inertial Shock / Shake Detection    │          │
│   │  - 1000 ms loop: Environmental Sensor Acquisition     │          │
│   │  - Custom Zero-Copy MQTT Serializer                   │          │
│   └───────────────────────────┬────────────────────────────┘          │
│                               │ SPI3                                  │
│   ┌───────────────────────────▼────────────────────────────┐          │
│   │      Inventek ISM43362-M3G-L44 Wi-Fi Module            │          │
│   └───────────────────────────┬────────────────────────────┘          │
└───────────────────────────────┼────────────────────────────────────────┘
                                │ IEEE 802.11 b/g/n (Local Wi-Fi)
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      LOCAL INDUSTRIAL GATEWAY / PC                     │
│                                                                        │
│   ┌────────────────────────────────────────────────────────┐          │
│   │             Eclipse Mosquitto MQTT Broker              │          │
│   │          Topics: /temperature, /humidite, /pression    │          │
│   └───────────────────────────┬────────────────────────────┘          │
│                               │ TCP 1883                              │
│   ┌───────────────────────────▼────────────────────────────┐          │
│   │               Node-RED Processing Pipeline             │          │
│   │  ┌───────────────────┐        ┌─────────────────────┐  │          │
│   │  │   UI Dashboard    │        │ SQLite Storage Node │  │          │
│   │  │ Gauges & Charts   │        │     sensors.db      │  │          │
│   │  └───────────────────┘        └──────────┬──────────┘  │          │
│   └──────────────────────────────────────────┼─────────────┘          │
│                                              │ SQL                    │
│   ┌──────────────────────────────────────────▼─────────────┐          │
│   │            Python Analytics & Visualization            │          │
│   │   plot_sensors.py  |  analyse_database.py (Pandas)     │          │
│   └────────────────────────────────────────────────────────┘          │
└────────────────────────────────────────────────────────────────────────┘
`

---

## 🔬 Hardware & Sensors Inventory

The **B-L475E-IOT01A** integrates a rich array of MEMS sensors directly on the board:

| Component | Function | Bus / Interface | Resolution / Range |
|---|---|---|---|
| **STM32L475VGT6** | Host Microcontroller (ARM Cortex-M4) | Internal Bus | 80 MHz, 100 DMIPS, 1 MB Flash |
| **HTS221** | Capacitive Digital Relative Humidity & Temp | I2C2 ( xBE) | 0 to 100% rH, -40 to +120 °C |
| **LPS22HB** | Piezoresistive Absolute Barometer | I2C2 ( xBA) | 260 to 1260 hPa (0.05 hPa RMS) |
| **LSM6DSL** | 3D Accelerometer & 3D Gyroscope | SPI3 / I2C2 | ±2/±4/±8/±16 g, ±125 to ±2000 dps |
| **LIS3MDL** | 3-axis Magnetic Field Sensor | I2C2 ( x3C) | ±4 to ±16 gauss |
| **ISM43362-M3G-L44**| 802.11 b/g/n Wi-Fi Module | SPI3 (hspi3) | Integrated TCP/IP stack with AT parser |

---

## 💻 Firmware Architecture

The firmware is developed in **C** using **STM32CubeIDE** and the ST **HAL / BSP** libraries.

### Dual-Rate Scheduling

The primary control loop implements dual-rate task execution without the overhead of an operating system:

1. **High-Frequency Loop (20 Hz / 50 ms)**:
   - Polls 3-axis accelerometer values (, a_y, a_z$).
   - Calculates the instantaneous squared norm $|a|^2 = a_x^2 + a_y^2 + a_z^2$.
   - Triggers a **SHAKE event** whenever $|a|^2 > 2\,250\,000\,\text{mg}^2$ (equivalent to $>1.5\,g$), enforcing a 1-second debounce cooldown.
2. **Low-Frequency Loop (1 Hz / 1000 ms)**:
   - Reads calibrated values from HTS221 (Temperature and Humidity) and LPS22HB (Pressure).
   - Converts floating-point telemetry to formatted ASCII strings.
   - Formats and transmits individual MQTT publish packets across topics.

`c
/* 50 ms High-Frequency Inertial Routine */
BSP_ACCELERO_AccGetXYZ(acc);
int32_t ax = acc[0], ay = acc[1], az = acc[2];
uint32_t m2 = (uint32_t)(ax * ax + ay * ay + az * az);

if (shake_hold > 0) {
    shake_hold--;
} else if (m2 > SHAKE_THRESHOLD_MG2) {
    uart_print("*** SHAKE detected (|a|^2 > 1.5g) ***\r\n");
    shake_hold = 20; /* 1 second debounce hold */
}

/* 1000 ms Telemetry Transmission Routine */
if (++tick_1s >= 20) {
    tick_1s = 0;
    float temp  = BSP_TSENSOR_ReadTemp();
    float hum   = BSP_HSENSOR_ReadHumidity();
    float press = BSP_PSENSOR_ReadPressure();

    MQTT_Publish("/temperature", t_str);
    MQTT_Publish("/humidite", h_str);
    MQTT_Publish("/pression", p_str);
}
`

### Wi-Fi Subsystem (Inventek ISM43362)

The Inventek module communicates via SPI3 through the es_wifi driver layer:
- **Initialization & Handshake**: Queries firmware revision and hardware MAC address.
- **Network Discovery**: Scans available access points (SSID, channel, RSSI, encryption mode).
- **Network Join**: Implements a 3-stage reconnect state machine with configurable retry delays.
- **Gateway Verification**: Pings the local default gateway to measure round-trip time (RTT).
- **Socket Allocation**: Opens a dedicated TCP socket towards the Mosquitto broker on port 1883.

### Lightweight Embedded MQTT Client

Rather than pulling heavy external MQTT libraries, the firmware features a minimal zero-dependency packet generator:
- **CONNECT Packet (MQTT_Connect)**: Sends a 23-byte fixed frame defining Protocol Name (MQTT), Protocol Level (4), Clean Session flag, 60s Keep-Alive, and Client Identifier (stm32l475).
- **PUBLISH Packet (MQTT_Publish)**: Computes remaining length, packs topic length, topic string, and payload into a single network packet sent over TCP via WIFI_SendData().

---

## 📊 Node-RED Dashboard & Pipeline

<p align="center">
  <img src="docs/images/nodered_dashboard.png" alt="Node-RED Live Dashboard" width="850"/>
</p>
<p align="center"><em>Real-time supervision dashboard: instantaneous circular gauges, multi-sensor trend charts, and SQLite database record table</em></p>

### Flow Pipeline Breakdown

<p align="center">
  <img src="docs/images/nodered_flow_architecture.png" alt="Node-RED Flow Architecture" width="850"/>
</p>

The visual flow (
ode-red/flows.json) handles data ingestion and routing:
1. **MQTT Input Nodes**: Listen to /temperature, /humidite, and /pression.
2. **Merging & Synchronization Node**: Aggregates asynchronous sensor topics into a synchronized state payload with timestamp.
3. **Gauge & Chart UI Widgets**: Real-time visualization with custom thresholds and unit displays.
4. **SQLite Insertion Node**: Performs relational inserts into measurements (timestamp, temperature, humidite, pression).
5. **Periodic Table Query**: Automatically refreshes the last 50 entries in an HTML/Angular historical table.

---

## 🗄 Data Storage & Relational Schema

The telemetry stream is permanently persisted into a local SQLite database (sensors.db).

### Schema Definition
`sql
CREATE TABLE IF NOT EXISTS measurements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature REAL NOT NULL,
    humidite    REAL NOT NULL,
    pression    REAL NOT NULL
);
`

### SQL Query Examples
`sql
-- Retrieve the latest 10 telemetry readings
SELECT id, timestamp, temperature, humidite, pression 
FROM measurements 
ORDER BY id DESC LIMIT 10;

-- Calculate hourly moving averages
SELECT strftime('%Y-%m-%d %H:00', timestamp) AS hour_window,
       ROUND(AVG(temperature), 2) AS avg_temp,
       ROUND(AVG(humidite), 2)    AS avg_hum,
       ROUND(AVG(pression), 1)    AS avg_pres
FROM measurements
GROUP BY hour_window
ORDER BY hour_window DESC;
`

---

## 📈 Statistical Analysis & Validation

A Python data analysis tool (	ools/analyse_database.py) was developed to validate telemetry integrity and evaluate system performance across test cycles.

<p align="center">
  <img src="docs/images/sensor_temporal_analysis.png" alt="Multi-Axis Sensor Telemetry Analysis" width="850"/>
</p>
<p align="center"><em>Temporal analysis generated via Matplotlib showing environmental parameters across validation cycles</em></p>

### Telemetry Summary

| Parameter | Unit | Mean | Min | Max | Std Dev |
|---|---|---|---|---|---|
| **Temperature** | °C | 27.65 | 26.10 | 29.80 | ± 0.62 |
| **Humidity** | % rH | 64.80 | 58.20 | 71.40 | ± 2.15 |
| **Pressure** | hPa | 1018.4 | 1014.2 | 1022.1 | ± 0.94 |

---

## 📁 Repository Structure

`
stm32l475-iot-nodered/
├── README.md                           # Comprehensive documentation
├── LICENSE                             # Showcase & academic license
├── .gitignore                          # Excludes credentials, binaries, caches
├── docs/
│   └── images/                         # Dashboard screenshots & analysis graphs
│       ├── nodered_dashboard.png
│       ├── nodered_flow_architecture.png
│       ├── sensor_temporal_analysis.png
│       ├── serial_telemetry_debug.png
│       └── simulator_testing.png
├── firmware/                           # STM32CubeIDE embedded project
│   ├── Core/
│   │   ├── Inc/
│   │   │   ├── main.h
│   │   │   ├── stm32l4xx_hal_conf.h
│   │   │   ├── stm32l4xx_it.h
│   │   │   └── wifi_credentials.example.h  # Sanitized credentials template
│   │   ├── Src/
│   │   │   ├── main.c                  # Core acquisition & MQTT firmware
│   │   │   ├── stm32l4xx_hal_msp.c
│   │   │   ├── stm32l4xx_it.c
│   │   │   ├── syscalls.c
│   │   │   ├── sysmem.c
│   │   │   └── system_stm32l4xx.c
│   │   └── Startup/
│   │       └── startup_stm32l475vgtx.s
│   ├── Drivers/                        # Hardware abstraction & wireless drivers
│   │   ├── BSP/                        # B-L475E-IOT01 & MEMS sensor drivers
│   │   └── WiFi/                       # Inventek ISM43362 eS-WiFi driver
│   ├── RL.ioc                          # STM32CubeMX hardware configuration
│   ├── STM32L475VGTX_FLASH.ld          # Flash linker script
│   ├── .project
│   └── .cproject
├── node-red/
│   └── flows.json                      # Exported Node-RED flow configuration
└── tools/                              # Simulation, testing & analytics utilities
    ├── mosquitto.conf                  # Mosquitto broker configuration
    ├── simulate_stm32.ps1              # Telemetry emulator for offline testing
    ├── plot_sensors.py                 # SQLite database query & Matplotlib visualizer
    ├── analyse_database.py             # Exploratory statistical analysis script
    ├── check_db.py                     # SQLite quick verification script
    └── sample_measurements.csv         # Sample dataset recorded from hardware
`

> **🔒 Security & Confidentiality Notice:** Real network passwords and personal hotspot keys are stripped from this repository. To compile and run on hardware, configure your local network settings inside irmware/Core/Inc/wifi_credentials.h based on the provided template.

---

## 🚀 Quickstart Guide

### 1. Mosquitto Broker Setup

Start the local MQTT broker using the provided configuration:
`powershell
cd tools
mosquitto -c mosquitto.conf -v
`

### 2. Node-RED Setup

1. Install required palette modules:
   `ash
   npm install node-red-dashboard node-red-node-sqlite
   `
2. Start Node-RED:
   `ash
   node-red
   `
3. Open http://localhost:1880, click **Menu ➔ Import**, and paste the contents of 
ode-red/flows.json.
4. Click **Deploy**. Access the live dashboard at http://localhost:1880/ui.

### 3. Firmware Build & Flash

1. Open **STM32CubeIDE** and import irmware/ as an existing Eclipse project.
2. Copy irmware/Core/Inc/wifi_credentials.example.h to wifi_credentials.h and configure your Wi-Fi SSID and password:
   `c
   #define WIFI_SSID     "Your_Network_SSID"
   #define WIFI_PASSWORD "Your_Network_Password"
   `
3. Build the project (Ctrl+B) and flash the **B-L475E-IOT01A** via ST-LINK.
4. Open a serial terminal (115200 baud, 8N1) on the virtual COM port to observe initialization and MQTT telemetry logs:

<p align="center">
  <img src="docs/images/serial_telemetry_debug.png" alt="STM32 Serial Console Telemetry" width="700"/>
</p>

### 4. Software Simulation (Hardware-Free Testing)

You can test the entire Node-RED pipeline, dashboard, and database without hardware using the included emulator:

`powershell
cd tools
.\simulate_stm32.ps1 -Count 60 -DelaySec 1
`

To visualize the captured SQLite database records in Python:
`ash
python tools/plot_sensors.py --last 30
`

---

## 👩‍💻 Author & Academic Attribution

**Eya Badri**  
- Diplôme National d'Ingénieur en Génie Électrique (3GE)  
- **École Nationale d'Ingénieurs de Tunis (ENIT)** — Université de Tunis El Manar  
- 📧 Contact: [eya.badri@etudiant-enit.utm.tn](mailto:eya.badri@etudiant-enit.utm.tn)  
- 🌐 GitHub: [github.com/eyabadri](https://github.com/eyabadri)

---

## 📜 License

This project is released under the **MIT License (Modified for Showcase)**. See [LICENSE](LICENSE) for terms.

© 2026 Eya Badri — All Rights Reserved.
