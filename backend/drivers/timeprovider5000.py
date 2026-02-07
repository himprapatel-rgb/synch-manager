"""Microchip TimeProvider 5000 driver for Synch-Manager.

Maps Microchip/Symmetricom SNMP MIBs to the common driver interface
for the TP5000 PTP grandmaster / SSU platform.
"""
import logging
from .base_driver import BaseDriver

logger = logging.getLogger(__name__)


class TimeProvider5000Driver(BaseDriver):
    """Driver for Microchip TimeProvider 5000."""

    NE_TYPE = 'timeprovider_5000'
    SUPPORTED_LINK_TYPES = ['ptp_synce', 'ptp']

    # OIDs (Microchip/Symmetricom enterprise MIB)
    OID_SYS_DESCR       = '1.3.6.1.2.1.1.1.0'
    OID_SYS_UPTIME      = '1.3.6.1.2.1.1.3.0'
    OID_SYS_NAME        = '1.3.6.1.2.1.1.5.0'
    OID_FW_VERSION      = '1.3.6.1.4.1.9070.1.2.5.1.1.1.0'
    OID_GNSS_STATUS     = '1.3.6.1.4.1.9070.1.2.5.1.2.1.0'
    OID_GNSS_SATELLITES  = '1.3.6.1.4.1.9070.1.2.5.1.2.2.0'
    OID_CLOCK_STATUS    = '1.3.6.1.4.1.9070.1.2.5.1.3.1.0'
    OID_ALARM_SUMMARY   = '1.3.6.1.4.1.9070.1.2.5.1.4.1.0'
    OID_PHASE_OFFSET_NS = '1.3.6.1.4.1.9070.1.2.5.1.5.1.0'
    OID_FREQ_OFFSET_PPB = '1.3.6.1.4.1.9070.1.2.5.1.5.2.0'

    def get_inventory(self, host: str, community: str) -> dict:
        return {
            'ne_type': self.NE_TYPE,
            'description': str(self.snmp_get(host, self.OID_SYS_DESCR, community) or ''),
            'hostname': str(self.snmp_get(host, self.OID_SYS_NAME, community) or ''),
            'firmware_version': str(self.snmp_get(host, self.OID_FW_VERSION, community) or ''),
            'uptime_ticks': int(self.snmp_get(host, self.OID_SYS_UPTIME, community) or 0),
            'link_type': 'ptp_synce',
        }

    def get_alarms(self, host: str, community: str) -> list[dict]:
        alarms = []
        alarm_summary = self.snmp_get(host, self.OID_ALARM_SUMMARY, community)
        if alarm_summary and int(alarm_summary) != 0:
            alarms.append({
                'alarm_type': 'TP5000_ALARM_ACTIVE',
                'severity': 'major',
                'detail': f'Alarm bitmap: {int(alarm_summary)}',
            })
        gnss = self.snmp_get(host, self.OID_GNSS_STATUS, community)
        if gnss and int(gnss) != 1:
            alarms.append({
                'alarm_type': 'GNSS_UNLOCK',
                'severity': 'critical',
                'detail': f'GNSS status: {int(gnss)}',
            })
        return alarms

    def get_performance(self, host: str, community: str) -> dict:
        phase = self.snmp_get(host, self.OID_PHASE_OFFSET_NS, community)
        freq = self.snmp_get(host, self.OID_FREQ_OFFSET_PPB, community)
        return {
            'phase_offset_ns': int(phase) if phase else None,
            'frequency_offset_ppb': int(freq) if freq else None,
            'link_type': 'ptp_synce',
        }

    def get_clock_quality(self, host: str, community: str) -> dict:
        clock_raw = self.snmp_get(host, self.OID_CLOCK_STATUS, community)
        val = int(clock_raw) if clock_raw else 0
        quality_map = {1: 'PRS', 2: 'PRC', 3: 'SSU_A', 4: 'SSU_B'}
        return {
            'quality_level': quality_map.get(val, 'DNU'),
            'clock_mode': val,
        }

    def get_gnss_status(self, host: str, community: str) -> dict:
        gnss = self.snmp_get(host, self.OID_GNSS_STATUS, community)
        sats = self.snmp_get(host, self.OID_GNSS_SATELLITES, community)
        locked = int(gnss) == 1 if gnss else False
        return {
            'has_gnss': True,
            'gnss_locked': locked,
            'satellites_tracked': int(sats) if sats else 0,
            'time_source': 'gnss' if locked else 'holdover',
        }
