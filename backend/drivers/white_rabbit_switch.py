"""White Rabbit Switch (WRS) driver for Synch-Manager.

Maps WR-SWITCH-MIB and WR-WRPC-MIB SNMP OIDs to the common
driver interface. Provides sub-nanosecond timing data for
performance monitoring, fault detection, and GNSS resilience.

OID references from WR-SWITCH-MIB / WR-WRPC-MIB:
  - wrsPtpClockOffsetPs : clock offset in picoseconds
  - wrsPtpRTT           : round-trip time
  - wrsPtpServoState    : servo state (TRACKING, HOLDOVER, etc.)
  - SFP diagnostic OIDs : temperature, TX/RX power
  - Port state OIDs     : WR Master / WR Slave role per port
"""
import logging
from .base_driver import BaseDriver

logger = logging.getLogger(__name__)


class WhiteRabbitSwitchDriver(BaseDriver):
    """Driver for CERN White Rabbit Switch (WRS) v4.x / v5.x."""

    NE_TYPE = 'white_rabbit_switch'
    SUPPORTED_LINK_TYPES = ['white_rabbit', 'ptp_synce', 'ptp']

    # -- WR-SWITCH-MIB OIDs ------------------------------------------
    OID_PTP_CLOCK_OFFSET_PS = '1.3.6.1.4.1.96.101.1.2.1.0'
    OID_PTP_RTT             = '1.3.6.1.4.1.96.101.1.2.2.0'
    OID_PTP_SERVO_STATE     = '1.3.6.1.4.1.96.101.1.2.3.0'
    OID_PTP_SERVO_UPDATES   = '1.3.6.1.4.1.96.101.1.2.4.0'
    # SFP diagnostics
    OID_SFP_TEMP_PREFIX     = '1.3.6.1.4.1.96.101.1.3.1.1'
    OID_SFP_TX_POWER_PREFIX = '1.3.6.1.4.1.96.101.1.3.1.2'
    OID_SFP_RX_POWER_PREFIX = '1.3.6.1.4.1.96.101.1.3.1.3'
    # Port state (WR Master=6, WR Slave=9, etc.)
    OID_PORT_STATE_PREFIX   = '1.3.6.1.4.1.96.101.1.4.1.1'
    # Standard MIBs for inventory
    OID_SYS_DESCR    = '1.3.6.1.2.1.1.1.0'
    OID_SYS_UPTIME   = '1.3.6.1.2.1.1.3.0'
    OID_SYS_NAME     = '1.3.6.1.2.1.1.5.0'
    OID_FW_VERSION   = '1.3.6.1.4.1.96.101.1.1.1.0'

    # Servo state value mapping
    SERVO_STATES = {
        0: 'UNINITIALIZED',
        1: 'SYNC_SEC',
        2: 'SYNC_NSEC',
        3: 'SYNC_PHASE',
        4: 'TRACK_PHASE',
        5: 'WAIT_OFFSET_STABLE',
    }

    # -- BaseDriver implementations ----------------------------------

    def get_inventory(self, host: str, community: str) -> dict:
        """Collect WRS inventory: firmware, uptime, hostname."""
        return {
            'ne_type': self.NE_TYPE,
            'description': str(self.snmp_get(host, self.OID_SYS_DESCR, community) or ''),
            'hostname': str(self.snmp_get(host, self.OID_SYS_NAME, community) or ''),
            'firmware_version': str(self.snmp_get(host, self.OID_FW_VERSION, community) or ''),
            'uptime_ticks': int(self.snmp_get(host, self.OID_SYS_UPTIME, community) or 0),
            'link_type': 'white_rabbit',
        }

    def get_alarms(self, host: str, community: str) -> list[dict]:
        """Check WR-specific alarm conditions."""
        alarms = []
        servo_raw = self.snmp_get(host, self.OID_PTP_SERVO_STATE, community)
        servo_val = int(servo_raw) if servo_raw is not None else -1
        servo_name = self.SERVO_STATES.get(servo_val, f'UNKNOWN({servo_val})')

        # Alarm if servo is not in TRACK_PHASE
        if servo_val != 4:
            alarms.append({
                'alarm_type': 'WR_SERVO_LOST_LOCK',
                'severity': 'critical' if servo_val <= 1 else 'major',
                'detail': f'Servo state: {servo_name}',
            })

        # Check SFP health on first 8 ports
        for port in range(1, 9):
            sfp_temp = self.snmp_get(
                host, f'{self.OID_SFP_TEMP_PREFIX}.{port}', community
            )
            if sfp_temp is not None and int(sfp_temp) > 70000:  # millidegrees
                alarms.append({
                    'alarm_type': 'WR_SFP_DEGRADED',
                    'severity': 'major',
                    'detail': f'Port {port} SFP temperature {int(sfp_temp)/1000:.1f}C',
                })
        return alarms

    def get_performance(self, host: str, community: str) -> dict:
        """Collect sub-nanosecond performance metrics from WR servo."""
        offset_ps = self.snmp_get(host, self.OID_PTP_CLOCK_OFFSET_PS, community)
        rtt = self.snmp_get(host, self.OID_PTP_RTT, community)
        servo_updates = self.snmp_get(host, self.OID_PTP_SERVO_UPDATES, community)
        servo_state = self.snmp_get(host, self.OID_PTP_SERVO_STATE, community)

        return {
            'clock_offset_ps': int(offset_ps) if offset_ps else None,
            'clock_offset_ns': int(offset_ps) / 1000.0 if offset_ps else None,
            'round_trip_time_ps': int(rtt) if rtt else None,
            'servo_state': self.SERVO_STATES.get(
                int(servo_state) if servo_state else -1, 'UNKNOWN'
            ),
            'servo_update_count': int(servo_updates) if servo_updates else 0,
            'link_type': 'white_rabbit',
        }

    def get_clock_quality(self, host: str, community: str) -> dict:
        """Determine clock quality from WR servo state."""
        servo_raw = self.snmp_get(host, self.OID_PTP_SERVO_STATE, community)
        servo_val = int(servo_raw) if servo_raw is not None else -1
        offset_ps = self.snmp_get(host, self.OID_PTP_CLOCK_OFFSET_PS, community)
        abs_offset = abs(int(offset_ps)) if offset_ps else 999999

        if servo_val == 4 and abs_offset < 1000:  # < 1ns
            quality = 'ePRTC_grade'
        elif servo_val == 4 and abs_offset < 100000:  # < 100ns
            quality = 'PRTC'
        elif servo_val >= 3:
            quality = 'PRC'
        else:
            quality = 'HOLDOVER'

        return {
            'quality_level': quality,
            'servo_locked': servo_val == 4,
            'offset_ps': abs_offset,
        }

    def get_gnss_status(self, host: str, community: str) -> dict:
        """WR switches may not have GNSS directly; check GM lock."""
        servo_raw = self.snmp_get(host, self.OID_PTP_SERVO_STATE, community)
        servo_val = int(servo_raw) if servo_raw is not None else -1
        return {
            'has_gnss': False,  # WR slaves get time via fiber
            'gnss_locked': False,
            'wr_servo_locked': servo_val == 4,
            'time_source': 'white_rabbit_fiber',
        }

    # -- WR-specific methods -----------------------------------------

    def get_port_roles(self, host: str, community: str,
                       num_ports: int = 18) -> dict:
        """Return port-level WR role (Master/Slave/Non-WR)."""
        PORT_ROLES = {6: 'WR_MASTER', 9: 'WR_SLAVE'}
        roles = {}
        for port in range(1, num_ports + 1):
            state = self.snmp_get(
                host, f'{self.OID_PORT_STATE_PREFIX}.{port}', community
            )
            val = int(state) if state is not None else 0
            roles[port] = PORT_ROLES.get(val, f'OTHER({val})')
        return roles

    def get_sfp_diagnostics(self, host: str, community: str,
                            num_ports: int = 18) -> list[dict]:
        """Collect per-port SFP optical diagnostics."""
        diagnostics = []
        for port in range(1, num_ports + 1):
            temp = self.snmp_get(
                host, f'{self.OID_SFP_TEMP_PREFIX}.{port}', community
            )
            tx_pwr = self.snmp_get(
                host, f'{self.OID_SFP_TX_POWER_PREFIX}.{port}', community
            )
            rx_pwr = self.snmp_get(
                host, f'{self.OID_SFP_RX_POWER_PREFIX}.{port}', community
            )
            diagnostics.append({
                'port': port,
                'temperature_c': int(temp) / 1000.0 if temp else None,
                'tx_power_dbm': int(tx_pwr) / 1000.0 if tx_pwr else None,
                'rx_power_dbm': int(rx_pwr) / 1000.0 if rx_pwr else None,
            })
        return diagnostics

    def get_asymmetry_data(self, host: str, community: str) -> dict:
        """Return WR link asymmetry calibration data for GNSS resilience."""
        rtt = self.snmp_get(host, self.OID_PTP_RTT, community)
        offset = self.snmp_get(host, self.OID_PTP_CLOCK_OFFSET_PS, community)
        return {
            'rtt_ps': int(rtt) if rtt else None,
            'measured_offset_ps': int(offset) if offset else None,
            'calibration_source': 'wr_hardware',
        }
