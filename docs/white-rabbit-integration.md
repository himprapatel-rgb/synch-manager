# White Rabbit Integration Guide

This document describes how Synch-Manager integrates with White Rabbit (WR) switches and endpoints to provide sub-nanosecond timing distribution across the synchronization network.

## 1. What is White Rabbit?

White Rabbit is an extension of IEEE 1588 (PTP) that achieves sub-nanosecond synchronization accuracy over standard Ethernet fiber links. Originally developed at CERN for particle physics experiments, it is now widely adopted in scientific facilities, financial trading, telecommunications, and defense/government timing networks.

Key characteristics:

- Sub-nanosecond accuracy (typically <100 ps) over fiber links up to 100+ km.
- Uses Synchronous Ethernet (SyncE) combined with PTP and precise phase measurement.
- Open-source hardware and firmware (OHWR - Open Hardware Repository).
- Deterministic, low-jitter timing distribution suitable for mission-critical applications.

## 2. Supported White Rabbit Devices

Synch-Manager supports the following WR device types through the `white_rabbit_switch.py` driver:

| Device Type | Description | Driver Support |
|-------------|-------------|----------------|
| WR Switch (WRS) | Core WR network switch (18-port typical) | Full SNMP via WR-SWITCH-MIB |
| WR-LEN | WR Length-compensated endpoint | Basic monitoring |
| WR-ZEN | WR Zero-delay endpoint for calibration | Basic monitoring |
| SPEC + FMC-DIO | WR PCI Express carrier + I/O mezzanine | Via custom OIDs |
| WR Calibrator | Calibration device for WR link asymmetry | Read-only status |

## 3. Architecture

### 3.1 WR Network Topology in Synch-Manager

```text
[GNSS Antenna] --> [PTP Grandmaster + WR Master Port]
                          |
                    WR Fiber Link (sub-ns)
                          |
                   [WR Switch (Core)]
                    /      |       \
          WR Fiber    WR Fiber    WR Fiber
              /          |             \
     [WR Switch]   [WR Switch]   [WR Endpoint]
      (Site A)      (Site B)     (Lab Equipment)
```

Synch-Manager discovers and monitors all WR devices in this hierarchy, tracking link status, synchronization accuracy, and timing distribution health.

### 3.2 Driver Architecture

The WR driver (`backend/drivers/white_rabbit_switch.py`) extends `BaseDriver` and communicates via SNMP using the WR-SWITCH-MIB:

```text
Synch-Manager Backend
       |
  WhiteRabbitSwitchDriver
       |
  SNMP (v2c/v3) --> WR-SWITCH-MIB OIDs
       |
  WR Switch / WR Endpoint
```

## 4. SNMP MIB Mapping

The driver maps to the following WR-SWITCH-MIB OID branches:

| OID Base | Purpose |
|----------|----------|
| `.1.3.6.1.4.1.96.101` | WR system and general status |
| `wrsPtpStatus` | PTP servo state and offset from master |
| `wrsPortStatusTable` | Per-port link and SFP status |
| `wrsSoftwareVersion` | Firmware version information |
| `wrsTemperature` | FPGA and board temperature sensors |
| `wrsTimingStatus` | Overall timing health and source |

### 4.1 Key OIDs Used

| Function | OID Suffix | Description |
|----------|-----------|-------------|
| PTP State | `wrsPtpServoState` | Current PTP servo state (TRACKING, FREERUNNING, etc.) |
| Offset | `wrsPtpPhaseOffset` | Phase offset from master in picoseconds |
| Round-trip | `wrsPtpRoundTrip` | Link round-trip time in picoseconds |
| Port Link | `wrsPortStatusLink` | Per-port link up/down status |
| Port SFP | `wrsPortStatusSfp` | SFP module presence and type |
| Temperature | `wrsTemperatureFPGA` | FPGA die temperature |
| Uptime | `wrsUptime` | System uptime in seconds |

## 5. FCAPS Integration

### 5.1 Fault Management

Alarms raised by the WR driver:

| Alarm Type | Severity | Trigger |
|------------|----------|----------|
| `WR_SERVO_NOT_TRACKING` | CRITICAL | PTP servo leaves TRACKING state |
| `WR_LINK_DOWN` | MAJOR | WR fiber link goes down on any port |
| `WR_OFFSET_EXCEEDED` | MAJOR | Phase offset exceeds configurable threshold (default: 1000 ps) |
| `WR_TEMPERATURE_HIGH` | MINOR | FPGA temperature exceeds safe range |
| `WR_SFP_REMOVED` | WARNING | SFP transceiver removed from active port |

### 5.2 Inventory Management

Discovery populates:
- WR switch model, firmware version, serial number
- Per-port SFP module details (vendor, wavelength, power)
- Link partner identification (connected WR device)
- Timing hierarchy position (master/slave/grandmaster)

### 5.3 Performance Management

Metrics collected at configurable intervals (default: 60s):

| Metric | Unit | Storage |
|--------|------|----------|
| Phase offset from master | picoseconds | TimescaleDB |
| Link round-trip time | picoseconds | TimescaleDB |
| SFP optical power (Tx/Rx) | dBm | TimescaleDB |
| FPGA temperature | Celsius | TimescaleDB |
| Frequency offset | ppb | TimescaleDB |

### 5.4 Configuration Management

Configurable parameters via Synch-Manager:
- PTP domain number
- WR calibration values per port
- SyncE quality level (QL) advertisement
- Alarm thresholds for offset, temperature, optical power
- Port enable/disable

## 6. White Rabbit + GNSS Peer Resilience

When White Rabbit links are available between timing nodes, GNSS Peer Resilience uses WR paths as preferred backup routes during GNSS outages:

1. Under normal operation, each site locks to its own GNSS receiver.
2. If a site loses GNSS, it can receive sub-nanosecond time from a neighbor over WR.
3. Because WR provides <1 ns accuracy (vs ~100 ns for standard PTP), holdover quality is dramatically better.
4. The Sync Mesh Score increases when WR backup paths are available.

### 6.1 Failover Priority

```text
Priority 1: Local GNSS (locked)
Priority 2: White Rabbit link from GNSS-locked neighbor
Priority 3: Standard PTP from GNSS-locked neighbor
Priority 4: Local oscillator holdover (CSAC > Rb > OCXO > TCXO)
Priority 5: eLoran (if available)
Priority 6: LEO PNT (if available)
```

## 7. Cesium + White Rabbit Distribution

For highest resilience, a PRS-4400 cesium clock can feed a WR grandmaster:

```text
[PRS-4400 Cesium] --10MHz/1PPS--> [WR Grandmaster]
                                        |
                                  WR Fiber Network
                                   /     |     \
                             [Site A] [Site B] [Site C]
```

This provides cesium-level accuracy distributed over WR fiber to all remote sites, fully independent of GNSS. Combined with War Mode, this architecture can sustain sub-nanosecond timing indefinitely without any satellite input.

## 8. API Endpoints

WR-specific data is accessible through the standard inventory and performance APIs:

- `GET /api/v1/inventory/network-elements/?ne_type=WRS` - List all WR switches
- `GET /api/v1/inventory/network-elements/{id}/` - WR switch detail with cards/ports
- `GET /api/v1/performance/series/?ne_id={id}&metric_type=WR_OFFSET` - WR offset history
- `GET /api/v1/fault/alarms/active/?network_element={id}` - Active WR alarms

## 9. Grafana Dashboard

Synch-Manager includes a pre-built Grafana dashboard for WR monitoring:

- WR network topology map with link status colors
- Phase offset time-series plots per WR link
- SFP optical power trending
- Temperature heatmap across all WR devices
- Alarm timeline overlay

## 10. Deployment Notes

- WR switches must have SNMP enabled with community string matching Synch-Manager config.
- For SNMPv3, configure USM credentials in the NE registration.
- WR-SWITCH-MIB should be loaded on the WR device firmware (standard in recent WRS releases).
- Network connectivity between Synch-Manager server and WR management interfaces is required (typically out-of-band management VLAN).
- Recommended polling interval: 30-60 seconds for performance, 10 seconds for fault detection.
