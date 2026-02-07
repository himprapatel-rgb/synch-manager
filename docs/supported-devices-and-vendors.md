# Supported Devices, Vendors, and Universal MIB Management

This document lists all major timing and synchronization vendors, their devices, atomic clocks, and how Synch-Manager achieves universal device support through automatic MIB compilation and SNMP auto-discovery.

## 1. Vendor and Device Catalog

### 1.1 Microchip (Microsemi / Symmetricom)

The broadest portfolio in the industry covering PTP grandmasters, SSUs, atomic clocks, and management software. [web:299][web:306]

#### PTP Grandmasters and Timing Nodes

| Device | Category | Key Features |
|--------|----------|-------------|
| TimeProvider 4100 (TP4100) | PTP Grandmaster / Gateway Clock | PTP, NTP, SyncE, PRTC-A/B, ePRTC capable, APTS, GNSS multi-constellation, profile support for telecom and utility networks. [web:296][web:300] |
| TimeProvider 5000 (TP5000) | PTP Grandmaster | Modular PTP/NTP grandmaster, GNSS receiver, BITS interfaces, legacy sync integration, TimePictra managed. [web:297][web:299] |
| TimeHub 5500 | PTP Boundary Clock / Fan-out | Expansion shelf for TP4100 providing high-density sync outputs. [web:299] |
| TimeProvider XT | Extension Shelf | Fan-out platform for high port density (E1/T1/CC outputs). [web:303] |
| Integrated GNSS Module (IGM) | Embedded GNSS Module | Compact GNSS timing module for integration into other systems. [web:303] |

#### SSU / BITS Systems

| Device | Category | Key Features |
|--------|----------|-------------|
| SSU 2000 / SSU 2000e | Synchronization Supply Unit | BITS/SSU for carrier networks, ETSI/ANSI variants, redundant architecture. [web:298][web:299] |

#### Atomic Clocks and Frequency Standards

| Device | Category | Key Features |
|--------|----------|-------------|
| 5071A | Cesium Primary Frequency Standard | Primary frequency standard with outstanding stability, 10 MHz/5 MHz/1PPS outputs, long-term contributor to UTC. [web:315][web:321] |
| TimeCesium 4400 (PRS-4400) | Cesium Primary Reference Source | Stratum 1 cesium for telecom, 10 MHz, 5 MHz, 1PPS, DS1/E1 outputs, RS-232 management. [web:241][web:249][web:252] |
| TimeCesium 4500 | Enhanced Cesium PRS | Optimized for 5G and modern networks, higher density and performance. [web:245][web:250] |
| SA.45s CSAC | Chip-Scale Atomic Clock | Ultra-small, low-power atomic clock for edge and tactical applications. [web:272][web:275] |

#### Management Interfaces

| Device | SNMP | RS-232 | CLI/SSH | Web GUI | TimePictra |
|--------|------|--------|---------|---------|-----------|
| TP4100 | v2c/v3 | Yes | Yes | Yes | Yes |
| TP5000 | v2c/v3 | Yes | Yes | Yes | Yes |
| SSU 2000 | v2c | Yes | TL1 | No | Yes |
| PRS-4400 | (via host) | Yes | No | No | No |
| 5071A | (via host) | Yes | No | No | No |

---

### 1.2 Meinberg

German manufacturer specializing in NTP servers and PTP grandmasters with the IMS modular LANTIME platform. [web:301][web:304][web:313]

#### IMS Platform (Modular)

| Device | Category | Key Features |
|--------|----------|-------------|
| LANTIME M4000 | Flagship PTP/NTP Platform | 4U modular chassis, redundant PSU, multiple GNSS and oscillator modules, high-density PTP and NTP. [web:304][web:313] |
| LANTIME M3000 | Large PTP/NTP Platform | 3U modular platform, multiple clock/I/O modules, SyncE support. [web:304][web:313] |
| LANTIME M1000 | 1U Modular Platform | Compact 1U IMS with module slots for GNSS, oscillators, and output cards. [web:313] |
| LANTIME M500 | DIN Rail IMS | Industrial DIN rail chassis for utility/substation deployments. [web:313] |

#### Fixed-Format Devices

| Device | Category | Key Features |
|--------|----------|-------------|
| LANTIME M900 | 1U PTP/NTP Server | High-performance NTP and PTP with multi-GNSS. [web:311][web:312] |
| LANTIME M600/MRS | 1U NTP Server | High-end NTP server with multiple reference options. [web:311][web:312] |
| LANTIME M400 | 1U NTP Server | Mid-range NTP server for enterprise/telecom. [web:311] |
| LANTIME M300 | Desktop NTP Server | Compact NTP server with GNSS. [web:311] |
| LANTIME M250 | Desktop NTP Server | Small NTP server with LCD front panel. [web:311] |
| LANTIME M200 | 1U NTP Server | Rackmount, GPS or DCF77 variants. [web:311] |
| LANTIME M100 | DIN Rail NTP Server | DIN rail NTP server for industrial environments. [web:311] |
| microSync | Compact PTP GM | Very small PTP grandmaster for edge. [web:312] |

#### IMS Modules (Examples)

| Module | Function |
|--------|---------|
| GNS/GPS | GNSS receiver module (GPS, Galileo, GLONASS, BeiDou). [web:313] |
| HPS100 | PTP/IEEE 1588 module. [web:313] |
| RSC | Rubidium oscillator module. [web:313] |

#### Management Interfaces

- SNMP v1/v2c/v3 (MEINBERG-LANTIME-MIB). [web:313]
- SSH CLI and HTTPS web GUI. [web:304][web:313]
- NTP/PTP monitoring and proprietary APIs.

---

### 1.3 Oscilloquartz (Adtran)

Swiss timing specialist (Adtran) with cesium clocks, PTP grandmasters, and embedded timing. [web:302][web:305][web:327]

#### Cesium and ePRTC

| Device | Category | Key Features |
|--------|----------|-------------|
| OSA 3200/3250 | Cesium Frequency Standards | Legacy cesium clocks for telecom. [web:327] |
| OSA ePRTC Solutions | Enhanced PRC/ePRTC | Combines cesium + GNSS + STL/LEO PNT. [web:302] |

#### PTP Grandmasters and BCs

| Device | Category | Key Features |
|--------|----------|-------------|
| OSA 5440 | Core GM | coreSync redundant PTP grandmaster for large networks. [web:327] |
| OSA 5430 | edgeSync+ GM | ePRTC-capable platform with multiple ref sources. [web:327] |
| OSA 5420 | Gateway GM | PTP grandmaster/gateway for aggregation. [web:327] |
| OSA 5410 Series | Compact GM/BC/APTS | GNSS, SyncE, PTP, APTS, Syncjack for advanced monitoring. [web:328][web:329] |
| OSA 5405 Series | accessSync GM | Miniature grandmaster for small cells and edge. [web:336] |
| OSA 5401 Series | SFP Grandmaster (SyncPlug) | SFP-based PTP grandmaster fitting into switches. [web:326][web:330][web:333] |

#### Management Interfaces

- SNMP v2c/v3 with vendor MIBs. [web:327]
- Web GUI and CLI. [web:329]
- Ensemble management platforms (Ensemble Controller / Sync Director). [web:302]

---

### 1.4 Protempis (Trimble Timing)

Timing products from the Trimble/Protempis portfolio. [web:334][web:340]

| Device | Category | Key Features |
|--------|----------|-------------|
| Thunderbolt PTP GM200/GM330 | PTP Grandmaster | Multi-GNSS timing GM for 4G/5G. [web:331][web:334] |
| Thunderbolt TS200 | NTP Server | NTP time server based on GPSDO. [web:337] |
| Thunderbolt E | GPS Disciplined Clock | 10 MHz + 1PPS GPSDO. [web:334] |
| ICM SMT 360, Resolution SMT GG | GNSS Modules | OEM timing receivers. [web:334] |
| Acutime 360 | GNSS Smart Antenna | Outdoor antenna with integrated receiver. [web:334] |

---

### 1.5 Safran (Orolia)

Defense and high-security timing. [web:269][web:273]

| Device | Category | Key Features |
|--------|----------|-------------|
| SecureSync | PTP/NTP GM with Security | Rugged, secure timing server with BroadShield GNSS threat detection. |
| VersaSync | Rugged Timing | SWaP-optimized timing for tactical platforms. |
| BroadShield | GNSS Defense | GNSS jamming/spoofing detection software integrated into receivers. |

Management: SNMP, web GUI, secure APIs.

---

### 1.6 EndRun Technologies

North American NTP/PTP servers. [web:307]

| Device | Category | Key Features |
|--------|----------|-------------|
| Sonoma D12 | PTP/NTP Server | GNSS, PTP, NTP, multiple Ethernet ports. |
| Sonoma C12 | Compact Server | Smaller platform for enterprise/SCADA. |
| Tycho II | High-End GNSS Time Server | Dual power, multiple outputs. |
| Meridian II | Frequency and Time Standard | Lab-grade standard. |

Management: SNMP, web GUI, CLI.

---

### 1.7 Calnex Solutions

Sync test instruments. [web:310][web:335][web:338]

| Device | Category | Key Features |
|--------|----------|-------------|
| Sentinel | Field Sync Tester | PTP, NTP, SyncE, Time Error measurement, GNSS & Rb. [web:332][web:338] |
| Paragon-X / Paragon-One | Lab Testers | PTP/NTP/SyncE test and emulation platforms. [web:335] |

---

### 1.8 Other Vendors (Summary)

| Vendor | Notable Devices | Category |
|--------|----------------|----------|
| Seiko Solutions | TF-4100, TimeServer | NTP/PTP servers. |
| Masterclock | GMR5000, NTP100 | NTP/PTP time displays and servers. |
| OPNT | Software PTP GM | Software-based grandmaster. |
| Timebeat | Open Time Server/Client | Open-source NTP/PTP solutions. |
| CASIC / local vendors | CS4000, CFS series | Cesium and rubidium standards. [web:319] |
| SRS, Spectratime, Frequency Electronics | FS725, iSource+, FE-5680A | Rubidium and CSAC standards. [web:319] |

---

## 2. Atomic Clocks Overview

### 2.1 Cesium Standards

| Model | Manufacturer | Accuracy | Interface |
|-------|-------------|----------|----------|
| 5071A | Microchip | ~5×10⁻¹³ | RS-232, front panel. [web:315][web:321] |
| TimeCesium 4400 | Microchip | ≤1×10⁻¹² | RS-232. [web:241][web:249][web:252] |
| TimeCesium 4500 | Microchip | ≤1×10⁻¹² | RS-232. [web:245][web:250] |
| OSA 3200/3350 | Oscilloquartz | ~10⁻¹²–10⁻¹³ | Various. [web:327] |
| CS4000 | CASIC | ~5×10⁻¹² | RS-232. [web:319] |

### 2.2 Rubidium and CSAC

| Model | Type | Notes |
|-------|------|-------|
| SA.45s | CSAC | Chip-scale atomic clock for tactical/edge use. [web:272][web:275] |
| FS725 | Rubidium | 10 MHz output, RS-232. |
| FE-5680A | Rubidium | OEM module, 10 MHz output. |
| iSource+ | Rubidium | Spectratime rubidium standard. [web:319] |

---

## 3. Universal MIB Management Engine

Synch-Manager is designed to manage **any** SNMP-capable timing device by compiling and using vendor MIB files.

### 3.1 Concept

- User uploads vendor MIB (.mib/.my).
- Backend compiles MIB using PySMI (part of PySNMP). [web:318][web:320]
- Compiled MIB is stored and indexed (OIDs, names, traps).
- Generic SNMP driver uses this compiled MIB to:
  - Walk and poll OIDs by name.
  - Decode traps into alarms.
  - Auto-generate monitoring templates.

### 3.2 MIB Upload Workflow

1. Upload MIB via web UI or REST:
   - `POST /api/v1/mibs/upload/`
2. System validates and compiles the MIB:
   - Resolves imports (SNMPv2-SMI, SNMPv2-TC, etc.). [web:316][web:320]
3. MIB Registry stores:
   - OID tree.
   - Object types and descriptions.
   - NOTIFICATION-TYPE (trap) definitions.
4. Synch-Manager suggests:
   - Polling list (status, performance, inventory).
   - Trap-to-alarm mappings.

### 3.3 Generic SNMP Driver

For any unknown device with SNMP:

- Reads `sysObjectID` and `sysDescr`.
- Matches enterprise OID to known vendor MIBs if available.
- If match:
  - Uses device MIB to poll recommended OIDs.
  - Automatically decodes traps into alarms.
- If no match:
  - Still polls standard MIB-II (interfaces, uptime, etc.).
  - User is prompted to upload the vendor MIB to unlock full support.

This architecture means **your app can manage any SNMP device** as soon as a MIB is available.

---
