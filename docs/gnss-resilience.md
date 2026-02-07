# GNSS Resilience and Continuity

## 1. Overview

Synch-Manager provides military-grade GNSS resilience capabilities to ensure continuous timing accuracy even during GNSS failures, jamming, or spoofing attacks. The system employs multiple redundant timing sources and intelligent failover mechanisms.

## 2. Multi-Source Timing Architecture

### 2.1 Primary Timing Sources

- **GNSS (GPS/Galileo/GLONASS/BeiDou)**: Primary reference with multi-constellation support
- **White Rabbit PTP Network**: Optical fiber synchronization via WR switches
- **Chip-Scale Atomic Clocks (CSAC)**: Holdover capability during GNSS outages
- **eLoran**: Terrestrial RF backup timing for critical infrastructure
- **LEO-PNT Satellites**: Low Earth Orbit positioning/navigation/timing

### 2.2 Timing Source Hierarchy

```
Priority 1: GNSS (when healthy, C/N0 > 35 dB-Hz, no spoofing detected)
Priority 2: White Rabbit PTP (fiber link, nanosecond accuracy)
Priority 3: CSAC (holdover mode, < 1μs drift per day)
Priority 4: eLoran (100-200ns accuracy)
Priority 5: LEO-PNT (backup constellation)
```

## 3. GNSS Health Monitoring

### 3.1 Real-Time Metrics

- **Carrier-to-Noise Ratio (C/N0)**: Per-satellite signal strength
- **Satellite Count**: Number of tracked satellites per constellation
- **Pseudorange Residuals**: Multipath and measurement errors
- **Position Stability**: Lat/lon drift detection
- **Time Offset**: Comparison with White Rabbit master clock

### 3.2 Threat Detection

#### Jamming Detection
- AGC level monitoring
- Sudden C/N0 drops across multiple satellites
- Spectrum analysis of RF bands

#### Spoofing Detection
- Clock jump detection (> 1ms)
- Impossible position jumps
- Satellite geometry anomalies
- Cross-validation with PTP/CSAC
- Cryptographic authentication (Galileo OSNMA, GPS M-code)

## 4. Peer Failover Mechanism

Synch-Manager implements a peer-based failover system where GNSS receivers share status information and coordinate timing source selection.

### 4.1 Peer Communication

```python
# Peer Status Exchange via SNMP/MQTT
class GNSSPeerStatus:
    peer_id: str
    gnss_locked: bool
    satellites_tracked: int
    c_no_avg: float
    position_lat: float
    position_lon: float
    time_source: str  # GNSS, WR, CSAC, eLoran, LEO
    trust_score: int  # 0-100
    last_update: datetime
```

### 4.2 Failover Algorithm

```
IF local_gnss.locked AND local_gnss.trust_score > 80:
    USE local_gnss AS primary
ELSE IF white_rabbit.available AND wr_link_delay < 10μs:
    USE white_rabbit AS primary
    NOTIFY peers: "GNSS degraded, using WR"
ELSE IF peer.gnss_locked AND peer.trust_score > 90:
    USE peer_gnss AS reference via PTP
    ACTIVATE csac FOR holdover
ELSE:
    ENTER csac_holdover_mode
    TRIGGER alarm: "All GNSS sources failed"
```

### 4.3 Peer Backup Delay Configuration

**Synch-Manager Settings:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `peer_failover_delay_sec` | 10 | Wait time before activating peer backup |
| `war_mode_threshold_pct` | 50 | Percentage of GNSS-denied nodes to trigger War Mode |
| `wr_mode_threshold_pct` | 50 | Percentage of nodes needed to activate War Mode |
| `gnss_poll_interval_sec` | 30 | How often to check GNSS status |
| `spoofing_position_threshold_m` | 100 | Position jump threshold for spoofing detection |

## 5. War Mode Activation

**War Mode** is triggered when a significant portion of the network detects GNSS failures or attacks.

### 5.1 War Mode Triggers

- ≥ 50% of nodes report GNSS spoofing/jamming
- ≥ 3 nodes in same geographic region report simultaneous GNSS failure
- Manual activation via operator command

### 5.2 War Mode Behavior

```yaml
war_mode_actions:
  - switch_to_wr_primary: true
  - enable_csac_holdover: true
  - activate_eloran_receivers: true
  - increase_peer_poll_rate: 5x
  - log_all_timing_sources: true
  - notify_operators: URGENT
  - disable_gnss_auto_relock: true  # Prevent spoofing attacks
```

### 5.3 Exit from War Mode

- Manual operator confirmation
- All nodes report GNSS health restored for > 30 minutes
- Cryptographic GNSS authentication (OSNMA) verified

## 6. Synch-Manager Resilience Settings

Configuration in `backend/config/settings.py`:

```python
GNSS_RESILIENCE = {
    'enabled': True,
    'peer_failover_delay_sec': 10,
    'peer_backup_enabled': True,
    'war_mode_threshold_pct': 50,
    'wr_mode_threshold_pct': 50,
    'gnss_poll_interval_sec': 30,
    'satellites_min': 4,
    'c_no_threshold_dbhz': 35,
    'spoofing_detection': {
        'enabled': True,
        'position_threshold_m': 100,
        'time_jump_threshold_ms': 1,
        'osnma_enabled': True,
    },
    'holdover_mode': {
        'csac_max_duration_hours': 72,
        'eloran_fallback': True,
        'leo_pnt_fallback': True,
    },
    'alarms': {
        'gnss_failure': 'CRITICAL',
        'spoofing_detected': 'URGENT',
        'csac_holdover': 'WARNING',
        'war_mode_active': 'CRITICAL',
    }
}
```

## 7. Grafana Dashboards

Synch-Manager provides pre-built dashboards for GNSS resilience:

- **GNSS Health Map**: Geographic map showing GNSS lock status per site with color coding.
- **Peer Timing Flow**: Sankey diagram showing which nodes are providing time to which neighbors.
- **Holdover Countdown**: Per-node countdown timers showing estimated time remaining in holdover.
- **GNSS Threat Monitor**: C/N0 plots, position stability, and threat event timeline.

## 8. API Endpoints

### 8.1 GNSS Status

```bash
GET /api/v1/inventory/network-elements/<id>/gnss-status
```

Response:
```json
{
  "gnss_locked": true,
  "satellites_tracked": 12,
  "c_no_avg_dbhz": 42.5,
  "position": {"lat": 51.5074, "lon": -0.1278},
  "time_source": "GNSS",
  "trust_score": 95,
  "spoofing_detected": false,
  "war_mode": false
}
```

### 8.2 Trigger War Mode

```bash
POST /api/v1/gnss/war-mode
{
  "action": "activate",
  "reason": "Multiple nodes reporting spoofing"
}
```

## 9. Implementation

### 9.1 Backend Components

- **`backend/apps/security/gnss_resilience.py`**: Core GNSS health monitoring
- **`backend/apps/security/peer_failover.py`**: Peer coordination logic
- **`backend/apps/security/war_mode.py`**: War Mode state machine
- **`backend/drivers/gnss_receiver.py`**: Generic GNSS receiver driver
- **`backend/drivers/csac_driver.py`**: Chip-Scale Atomic Clock interface

### 9.2 Frontend Components

- **`frontend/src/components/GNSSHealthMap.jsx`**: Interactive map
- **`frontend/src/components/PeerTimingFlow.jsx`**: Peer relationship diagram
- **`frontend/src/components/WarModeControl.jsx`**: War Mode activation panel

## 10. Testing

### 10.1 GNSS Outage Simulation

```bash
# Simulate GNSS jamming on node
curl -X POST http://synch-manager:8000/api/v1/testing/simulate-gnss-failure/<node_id>
```

### 10.2 Peer Failover Test

1. Disable GNSS on Node A
2. Verify Node A switches to White Rabbit
3. Disable WR on Node A
4. Verify Node A pulls time from Peer Node B
5. Verify CSAC holdover activates if all sources fail

---

**Last Updated**: 2025
**Version**: 1.0
**Maintainer**: Synch-Manager Team
