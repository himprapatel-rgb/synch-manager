# Sync Digital Twin — Built-in Network Simulator

## Overview

The Sync Digital Twin is a built-in simulation engine that creates virtual timing networks
inside Synch-Manager. It allows development, testing, training, and sales demonstrations
without any physical hardware.

Virtual Network Elements (NEs) behave identically to real NEs from the perspective of the
dashboard, alarms, performance charts, and all logic (Peer Resilience, War Mode, Zero Trust).
The only difference is that their telemetry comes from the scenario engine instead of SNMP. [file:2][file:3]

## Use Cases

| Use Case | Description |
|----------|-------------|
| Development | Build and test GNSS security, Peer Resilience, War Mode without hardware |
| Sales demos | Show customers how their network reacts to jamming, spoofing, fiber cuts |
| Training | Engineers practice sync management on safe virtual networks |
| Pre-deployment | Model a customer's planned network, simulate failures, find weak points |
| CI/CD testing | Every code commit runs automated scenarios to verify nothing is broken |
| Certification | Run standardized failure scenarios and generate compliance reports |

The idea is similar to modern network “digital twins”, where a virtual copy of the network is
used for testing and validation before deploying changes in production. [web:409]

## Architecture

```text
┌───────────────────────────────────────────────────────┐
│                  Synch-Manager Backend                  │
│                                                        │
│  ┌──────────────────┐     ┌──────────────────────────┐ │
│  │  Real NE Drivers  │     │  Digital Twin Engine      │ │
│  │  (SNMP, serial)   │     │                          │ │
│  │                   │     │  ┌────────────────────┐  │ │
│  │  TP4100 driver    │     │  │ Virtual NE Models  │  │ │
│  │  Meinberg driver  │     │  │ (same fields as    │  │ │
│  │  OSA driver       │     │  │  real NEs)         │  │ │
│  │  Generic SNMP     │     │  └────────┬───────────┘  │ │
│  │                   │     │           │              │ │
│  └───────┬───────────┘     │  ┌────────▼───────────┐  │ │
│          │                 │  │ Scenario Engine     │  │ │
│          │                 │  │ (timed events that  │  │ │
│          │                 │  │  change NE state)   │  │ │
│          │                 │  └────────┬───────────┘  │ │
│          │                 │           │              │ │
│          │                 │  ┌────────▼───────────┐  │ │
│          │                 │  │ GNSS Simulator     │  │ │
│          │                 │  │ + Holdover Engine  │  │ │
│          │                 │  └────────┬───────────┘  │ │
│          │                 └───────────┼──────────────┘ │
│          │                             │                │
│  ┌───────▼─────────────────────────────▼──────────────┐ │
│  │          Unified Data Layer                         │ │
│  │    (same DB tables for real and virtual NEs)        │ │
│  │    NE table:  is_virtual = True / False             │ │
│  └────────────────────────┬───────────────────────────┘ │
│                           │                             │
│  ┌────────────────────────▼───────────────────────────┐ │
│  │    REST API + WebSocket (dashboard sees both)       │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘


Real NEs are managed by vendor-specific and generic SNMP drivers. [file:2][file:3]

Virtual NEs are managed by the Digital Twin Engine.

Both share the same data model and database tables (NE, alarms, performance, GNSS status).

Virtual NE State Model
Every virtual NE maintains the same state that a real NE exposes via SNMP/CLI, so all
Synch-Manager features work identically for virtual and real NEs. [file:2][file:3]

Identity
ne_id: int — Auto-generated unique ID

ne_name: str — User-defined name (e.g. "Site-A-GM")

ne_type: str — Device type (e.g. "TimeProvider 4100", "LANTIME M3000")

vendor: str — Manufacturer (e.g. "Microchip", "Meinberg")

is_virtual: bool — Always True for digital twin NEs

ip_address: str — Simulated IP address

location: str — Site name or coordinates

serial_number: str — Simulated serial

firmware_version: str — Simulated firmware

Management
managed: bool — Whether Synch-Manager is managing the NE

reachable: bool — For virtual NEs, usually True unless scenario sets it to False

uptime_seconds: int — Seconds since the virtual NE was “powered on”

GNSS Status
lock_state: LOCKED | ACQUIRING | UNLOCKED

num_satellites: int — 0–32

avg_cn0: float — Carrier-to-noise ratio in dB-Hz (healthy: 35–50)

constellations: list of str — Active constellations (GPS, Galileo, GLONASS, BeiDou)

hdop: float — Horizontal dilution of precision

position_valid: bool — Whether position fix is valid

antenna_status: OK | SHORT | OPEN

jam_indicator: float — 0.0 (clean) to 1.0 (heavy jamming)

spoof_indicator: float — 0.0 (clean) to 1.0 (confirmed spoofing)

osnma_status: AUTHENTICATED | NOT_AVAILABLE | FAILED

These fields are enough to test GNSS jamming/spoofing detection and GNSS-aware logic
in Synch-Manager. [web:413][web:414]

PTP Status
clock_class: int — 6 (GNSS locked), 7 (holdover), 248 (free-run), etc.

clock_accuracy: str — IEEE 1588 accuracy enum (e.g. "0x21" = 100 ns)

port_state: MASTER | SLAVE | PASSIVE | LISTENING

gm_clock_id: str — Grandmaster clock identity (8-byte hex)

time_offset_ns: float — Current offset from reference

path_delay_ns: float — Measured path delay

num_ptp_clients: int — Number of connected PTP clients

synce_status: LOCKED | HOLDOVER | FREE_RUN

Oscillator / Clock Status
oscillator_type: OCXO | RUBIDIUM | CESIUM | CSAC

mode: NORMAL | HOLDOVER | FREE_RUN | WARMUP

holdover_start_time: datetime — When holdover began

holdover_elapsed_seconds: int — Seconds since holdover started

estimated_time_error_ns: float — Computed by the holdover drift model

frequency_offset_ppb: float — Current frequency offset

beam_status: NORMAL | DEGRADED | FAILED (cesium only)

tube_hours: int — Cesium tube operating hours

tube_life_percent: float — Cesium tube life percentage remaining

Performance
current_mtie_ns: float — Maximum Time Interval Error

current_tdev_ns: float — Time Deviation

phase_error_ns: float — Instantaneous phase error

Links
connected_to: list of NE IDs this NE is linked to

link_type: PTP | SYNCE | NTP | WHITE_RABBIT

link_state: UP | DOWN

link_delay_ns: float — Simulated link delay

Holdover Drift Model
The Digital Twin uses a simple, validated holdover model based on typical Allan Deviation
and aging rates for different oscillator types. [web:293][web:290]

Time error after time T (seconds) is approximated as:

Time Error
(
T
)
≈
f
offset
×
T
+
a
aging
×
T
2
2
Time Error(T)≈f 
offset
 ×T+ 
2
a 
aging
 ×T 
2
 
 
Where:

f
offset
f 
offset
  is initial frequency offset (approx. ADEV at 1 s).

a
aging
a 
aging
  is aging rate per second.

Example Holdover Estimates
Using realistic oscillator parameters, we get approximate time errors:

Oscillator	1 hour	6 hours	24 hours	72 hours
OCXO	~44 ns	~486 ns	~5.2 μs	~41.5 μs
Rubidium	~108 ns	~662 ns	~2.8 μs	~9.7 μs
CSAC	~542 ns	~3.3 μs	~14.3 μs	~50.5 μs
Cesium	~36 ns	~216 ns	~864 ns	~2.6 μs
These numbers are in the expected range for telecom-grade oscillators and are enough
for realistic software simulations of holdover behavior. [web:293][web:290]

Scenario Engine
Scenarios control how virtual NEs change over time. They are defined as JSON objects
with time-offset events applied to specific parameters.

Scenario Format (Example)
json
{
  "name": "Regional GNSS Jamming - North Sites",
  "description": "Progressive GNSS jamming affecting 3 sites over 30 minutes",
  "duration_minutes": 120,
  "events": [
    {
      "time_offset_seconds": 0,
      "description": "Normal operation",
      "targets": []
    },
    {
      "time_offset_seconds": 300,
      "description": "Site A: C/N0 starts degrading",
      "targets": [
        {
          "virtual_ne": "site_a_tp4100",
          "parameter": "gnss.avg_cn0",
          "transition": "linear_decrease",
          "from_value": 45.0,
          "to_value": 20.0,
          "duration_seconds": 180
        }
      ]
    },
    {
      "time_offset_seconds": 480,
      "description": "Site A: GNSS lock lost, holdover begins",
      "targets": [
        {
          "virtual_ne": "site_a_tp4100",
          "parameter": "gnss.lock_state",
          "transition": "instant",
          "to_value": "UNLOCKED"
        },
        {
          "virtual_ne": "site_a_tp4100",
          "parameter": "clock.mode",
          "transition": "instant",
          "to_value": "HOLDOVER"
        },
        {
          "virtual_ne": "site_a_tp4100",
          "parameter": "clock.holdover_drift_model",
          "transition": "instant",
          "to_value": "OCXO"
        }
      ]
    }
  ]
}
Transition Types
instant — Value changes immediately at the event time.

linear_decrease — Value decreases linearly over duration_seconds.

linear_increase — Value increases linearly over duration_seconds.

exponential_decay — Value decays exponentially (for C/N0 fades).

random_walk — Value fluctuates around a center (for noise-like behavior).

The scenario engine runs in a background loop and, at each tick (e.g. 1 second), it:

Computes the current scenario time.

Applies any events scheduled at or before that time.

Updates virtual NE states (GNSS, clock, links, etc.).

Triggers alarm generation and performance updates.

Pre-Built Scenarios
The following scenarios are planned as built-in JSON files:

gnss_jamming_single_site.json — Jamming at one site, progressive C/N0 loss.

gnss_spoofing_slow_drift.json — One site receives spoofed GNSS, time drifts slowly. [web:413][web:410]

regional_gnss_denial.json — 50%+ sites lose GNSS simultaneously (War Mode trigger).

fiber_cut.json — PTP link between two sites goes down.

cesium_tube_degradation.json — PRS-4400 beam tube degrades over hours.

oscillator_holdover_race.json — Multiple sites in holdover, different oscillators.

leap_second.json — Simulated UTC leap second event across all NEs.

cascading_failure.json — GNSS loss + fiber cut + oscillator drift combined.

These scenarios test the resilience and security features of Synch-Manager under a
wide variety of conditions.

Auto-Generated Alarms
When the scenario engine changes a virtual NE’s state, alarms are raised automatically.
Alarms from virtual NEs appear in the same alarm viewer as alarms from real NEs. [file:2][file:3]

Example Mappings
gnss.lock_state → UNLOCKED → CRITICAL: GNSS Lock Lost

gnss.avg_cn0 < threshold → MAJOR: GNSS Signal Degraded

jam_indicator > threshold → CRITICAL: GNSS Jamming Detected

spoof_indicator > threshold → CRITICAL: GNSS Spoofing Suspected

clock.mode → HOLDOVER → MAJOR: Clock in Holdover

estimated_time_error_ns > SLA → CRITICAL: Time Error Exceeds SLA

beam_status → DEGRADED/FAILED → MAJOR/CRITICAL: Cesium Tube Degradation/Failure

link_state → DOWN → CRITICAL: Sync Link Down

reachable → False → CRITICAL: NE Unreachable

Alarm severities and thresholds are configurable to match operator policies.

API Endpoints (Concept)
The Digital Twin will be exposed via REST APIs so the frontend and external systems can
control simulations.

Topology
POST /api/v1/digital-twin/topologies/ — Create a virtual topology.

GET /api/v1/digital-twin/topologies/ — List virtual topologies.

GET /api/v1/digital-twin/topologies/{id}/ — Get topology details.

DELETE /api/v1/digital-twin/topologies/{id}/ — Delete a virtual topology.

POST /api/v1/digital-twin/topologies/{id}/nes/ — Add virtual NE.

POST /api/v1/digital-twin/topologies/{id}/links/ — Add link between NEs.

Scenarios
POST /api/v1/digital-twin/scenarios/ — Upload a scenario JSON.

GET /api/v1/digital-twin/scenarios/ — List scenarios.

GET /api/v1/digital-twin/scenarios/{id}/ — Get scenario details.

POST /api/v1/digital-twin/scenarios/{id}/start/ — Start a scenario.

POST /api/v1/digital-twin/scenarios/{id}/pause/ — Pause a scenario.

POST /api/v1/digital-twin/scenarios/{id}/stop/ — Stop and reset.

GET /api/v1/digital-twin/scenarios/{id}/status/ — Get progress.

Virtual NE State
GET /api/v1/digital-twin/nes/{ne_id}/state/ — Full virtual NE state.

GET /api/v1/digital-twin/nes/{ne_id}/gnss/ — GNSS state only.

GET /api/v1/digital-twin/nes/{ne_id}/ptp/ — PTP state only.

GET /api/v1/digital-twin/nes/{ne_id}/clock/ — Clock/oscillator state only.

Virtual NEs also appear in the standard NE endpoints:

GET /api/v1/nes/ — returns both real and virtual NEs (filter with ?is_virtual=true).

GET /api/v1/alarms/ — returns alarms from both real and virtual NEs.

File Structure
Planned backend structure:

text
backend/digital_twin/
  __init__.py
  models.py              # VirtualTopology, VirtualNE, VirtualLink, Scenario
  engine.py              # Main simulation loop
  gnss_simulator.py      # GNSS status generation
  holdover_engine.py     # Oscillator drift computation
  alarm_generator.py     # Auto-generates alarms from state changes
  performance_engine.py  # Computes MTIE/TDEV from time error trajectory
  api.py                 # REST endpoints
  serializers.py         # DRF serializers
  scenarios/
    gnss_jamming_single_site.json
    gnss_spoofing_slow_drift.json
    regional_gnss_denial.json
    fiber_cut.json
    cesium_tube_degradation.json
    oscillator_holdover_race.json
    leap_second.json
    cascading_failure.json
This design is intentionally consistent with existing FCAPS concepts used in
commercial tools like TimePictra, but extends them with a built-in digital twin. [file:2][file:3]






