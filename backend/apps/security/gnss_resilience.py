"""GNSS Resilience and Anti-Spoofing/Anti-Jamming Module

Military-grade GNSS threat detection and mitigation for synch-manager.
Provides multi-constellation monitoring, peer resilience, and automatic
failover to backup timing sources.
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class GNSSThreatType(Enum):
    """Types of GNSS threats"""
    JAMMING = 'jamming'
    SPOOFING = 'spoofing'
    MEACONING = 'meaconing'  # Delayed rebroadcast attack
    SIGNAL_LOSS = 'signal_loss'
    MULTIPATH = 'multipath'
    IONOSPHERIC = 'ionospheric_disturbance'
    CLOCK_JUMP = 'clock_jump'  # Sudden time offset
    

class GNSSSeverity(Enum):
    """Threat severity levels"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class GNSSConstellation(Enum):
    """Supported GNSS constellations"""
    GPS = 'gps'
    GLONASS = 'glonass'
    GALILEO = 'galileo'
    BEIDOU = 'beidou'
    QZSS = 'qzss'
    IRNSS = 'irnss'


class GNSSMetrics:
    """GNSS signal quality metrics"""
    
    def __init__(self):
        self.cn0_db_hz: float = 0.0  # Carrier-to-noise ratio
        self.satellites_visible: int = 0
        self.satellites_used: int = 0
        self.hdop: float = 99.0  # Horizontal dilution of precision
        self.pdop: float = 99.0  # Position dilution of precision
        self.tdop: float = 99.0  # Time dilution of precision
        self.fix_quality: int = 0  # 0=no fix, 1=GPS, 2=DGPS, 4=RTK
        self.age_of_correction: float = 0.0
        self.timestamp: datetime = datetime.now()


class GNSSThreatDetector:
    """Military-grade GNSS threat detection engine"""
    
    # Detection thresholds
    JAMMING_CN0_THRESHOLD = 30.0  # dB-Hz
    SPOOFING_CLOCK_JUMP_THRESHOLD = 100e-6  # 100 microseconds
    SIGNAL_LOSS_TIMEOUT = 10  # seconds
    PEER_DIVERGENCE_THRESHOLD = 50e-6  # 50 microseconds
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.last_metrics: Dict[GNSSConstellation, GNSSMetrics] = {}
        self.threat_history: List[Dict] = []
        self.baseline_cn0: Dict[GNSSConstellation, float] = {}
        self.peer_timing_sources: List[str] = []
        self.last_time_offset: Optional[float] = None
        
    def analyze_signal(self, constellation: GNSSConstellation, 
                      metrics: GNSSMetrics) -> Optional[Dict]:
        """Analyze GNSS signal for threats"""
        
        threats = []
        
        # Jamming detection - significant CN0 drop
        if constellation in self.baseline_cn0:
            cn0_drop = self.baseline_cn0[constellation] - metrics.cn0_db_hz
            if cn0_drop > 10.0:  # 10 dB drop
                threats.append({
                    'type': GNSSThreatType.JAMMING,
                    'severity': self._calculate_jamming_severity(cn0_drop),
                    'details': f'CN0 drop: {cn0_drop:.1f} dB-Hz'
                })
        else:
            # Establish baseline
            self.baseline_cn0[constellation] = metrics.cn0_db_hz
        
        # Low signal quality
        if metrics.cn0_db_hz < self.JAMMING_CN0_THRESHOLD:
            threats.append({
                'type': GNSSThreatType.JAMMING,
                'severity': GNSSSeverity.HIGH,
                'details': f'Low CN0: {metrics.cn0_db_hz:.1f} dB-Hz'
            })
        
        # Poor geometry (high DOP values)
        if metrics.tdop > 5.0:
            threats.append({
                'type': GNSSThreatType.MULTIPATH,
                'severity': GNSSSeverity.MEDIUM,
                'details': f'High TDOP: {metrics.tdop:.2f}'
            })
        
        # Signal loss
        if metrics.satellites_used < 4:
            threats.append({
                'type': GNSSThreatType.SIGNAL_LOSS,
                'severity': GNSSSeverity.CRITICAL,
                'details': f'Only {metrics.satellites_used} satellites'
            })
        
        self.last_metrics[constellation] = metrics
        
        if threats:
            threat_event = {
                'device_id': self.device_id,
                'constellation': constellation.value,
                'threats': threats,
                'timestamp': metrics.timestamp
            }
            self.threat_history.append(threat_event)
            return threat_event
        
        return None
    
    def detect_spoofing(self, time_offset: float, 
                       peer_offsets: List[float]) -> Optional[Dict]:
        """Detect spoofing via peer resilience and clock jump detection"""
        
        threats = []
        
        # Clock jump detection
        if self.last_time_offset is not None:
            jump = abs(time_offset - self.last_time_offset)
            if jump > self.SPOOFING_CLOCK_JUMP_THRESHOLD:
                threats.append({
                    'type': GNSSThreatType.CLOCK_JUMP,
                    'severity': GNSSSeverity.CRITICAL,
                    'details': f'Time jump: {jump*1e6:.1f} microseconds'
                })
        
        # Peer divergence detection
        if len(peer_offsets) >= 2:
            mean_offset = sum(peer_offsets) / len(peer_offsets)
            max_divergence = max(abs(offset - mean_offset) for offset in peer_offsets)
            
            if max_divergence > self.PEER_DIVERGENCE_THRESHOLD:
                threats.append({
                    'type': GNSSThreatType.SPOOFING,
                    'severity': GNSSSeverity.HIGH,
                    'details': f'Peer divergence: {max_divergence*1e6:.1f} us'
                })
        
        self.last_time_offset = time_offset
        
        if threats:
            return {
                'device_id': self.device_id,
                'threats': threats,
                'timestamp': datetime.now()
            }
        
        return None
    
    def _calculate_jamming_severity(self, cn0_drop: float) -> GNSSSeverity:
        """Calculate jamming severity based on CN0 drop"""
        if cn0_drop > 20:
            return GNSSSeverity.CRITICAL
        elif cn0_drop > 15:
            return GNSSSeverity.HIGH
        elif cn0_drop > 10:
            return GNSSSeverity.MEDIUM
        else:
            return GNSSSeverity.LOW
    
    def get_threat_summary(self, time_window: timedelta = timedelta(hours=1)) -> Dict:
        """Get threat summary for recent time window"""
        cutoff = datetime.now() - time_window
        recent_threats = [
            threat for threat in self.threat_history 
            if threat['timestamp'] > cutoff
        ]
        
        threat_counts = {}
        for event in recent_threats:
            for threat in event['threats']:
                threat_type = threat['type'].value
                threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1
        
        return {
            'total_events': len(recent_threats),
            'threat_counts': threat_counts,
            'time_window': str(time_window)
        }


class GNSSResilienceManager:
    """Manages GNSS resilience and failover strategies"""
    
    def __init__(self):
        self.detectors: Dict[str, GNSSThreatDetector] = {}
        self.backup_sources = [
            'eloran',
            'leo_pnt',  # LEO satellite PNT
            'csac',     # Chip-Scale Atomic Clock
            'white_rabbit',
            'holdover'
        ]
        self.current_backup: Optional[str] = None
        self.failover_history: List[Dict] = []
    
    def register_detector(self, device_id: str) -> GNSSThreatDetector:
        """Register a new GNSS threat detector"""
        detector = GNSSThreatDetector(device_id)
        self.detectors[device_id] = detector
        return detector
    
    def initiate_failover(self, threat_event: Dict, reason: str) -> str:
        """Initiate failover to backup timing source"""
        
        # Select best available backup
        for backup in self.backup_sources:
            if self._is_backup_available(backup):
                self.current_backup = backup
                
                failover_event = {
                    'timestamp': datetime.now(),
                    'from': 'gnss',
                    'to': backup,
                    'reason': reason,
                    'threat_event': threat_event
                }
                self.failover_history.append(failover_event)
                
                logger.critical(
                    f"GNSS failover initiated: {reason}. "
                    f"Switching to {backup}"
                )
                
                return backup
        
        # No backup available - enter holdover
        self.current_backup = 'holdover'
        logger.critical("No backup timing source available - entering holdover mode")
        return 'holdover'
    
    def _is_backup_available(self, backup: str) -> bool:
        """Check if backup timing source is available"""
        # This would integrate with actual backup system status
        # For now, return True for all except current
        return backup != self.current_backup
    
    def get_resilience_status(self) -> Dict:
        """Get overall GNSS resilience status"""
        status = {
            'active_detectors': len(self.detectors),
            'current_source': 'gnss' if not self.current_backup else self.current_backup,
            'backup_sources_available': [
                src for src in self.backup_sources 
                if self._is_backup_available(src)
            ],
            'recent_failovers': len(self.failover_history),
            'threat_summary': {}
        }
        
        # Aggregate threat summaries from all detectors
        for device_id, detector in self.detectors.items():
            summary = detector.get_threat_summary()
            if summary['total_events'] > 0:
                status['threat_summary'][device_id] = summary
        
        return status


# Global resilience manager instance
resilience_manager = GNSSResilienceManager()
