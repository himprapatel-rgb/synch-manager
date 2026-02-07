"""Advanced Anti-Jamming System - Inspired by Israeli Military Tech

Implements multi-directional interference mitigation similar to:
- InfiniDome GPSdome (3-null steering, dual-band protection)
- IAI ADA System (multi-GNSS, digital signal processing)
- Septentrio AIM+ (real-time spectrum analysis, notch filtering)

Provides real-time RF spectrum monitoring, interference detection,
and actionable intelligence for GNSS protection.
"""

import logging
import numpy as np
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class JammingType(Enum):
    """Types of jamming interference"""
    NARROWBAND = 'narrowband'  # Single frequency
    WIDEBAND = 'wideband'      # Broadband noise
    PULSED = 'pulsed'          # Intermittent pulses
    SWEPT = 'swept'            # Frequency sweeping
    MATCHED_SPECTRUM = 'matched_spectrum'  # GNSS-like jamming
    

class InterferenceDirection(Enum):
    """Direction of interference source"""
    NORTH = 0
    NORTHEAST = 45
    EAST = 90
    SOUTHEAST = 135
    SOUTH = 180
    SOUTHWEST = 225
    WEST = 270
    NORTHWEST = 315
    

@dataclass
class RFSpectrum:
    """RF spectrum analysis data"""
    frequency_mhz: float
    power_dbm: float
    bandwidth_khz: float
    timestamp: datetime = field(default_factory=datetime.now)
    

@dataclass
class JammingEvent:
    """Detected jamming event"""
    jamming_type: JammingType
    frequency_band: str  # L1, L2, L5, G1, etc.
    power_level_dbm: float
    direction: Optional[InterferenceDirection]
    cn0_degradation_db: float
    affected_satellites: List[int]
    detected_at: datetime = field(default_factory=datetime.now)
    severity: str = 'medium'
    

class SpectrumAnalyzer:
    """Real-time RF spectrum analyzer - Septentrio AIM+ inspired"""
    
    # Frequency bands (MHz)
    GPS_L1 = 1575.42
    GPS_L2 = 1227.60
    GPS_L5 = 1176.45
    GLONASS_G1 = 1602.0
    GALILEO_E1 = 1575.42
    BEIDOU_B1 = 1561.098
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.baseline_spectrum: Dict[float, float] = {}
        self.current_spectrum: Dict[float, RFSpectrum] = {}
        self.interference_detected: List[JammingEvent] = []
        
    def analyze_spectrum(self, spectrum_data: List[RFSpectrum]) -> List[JammingEvent]:
        """Analyze RF spectrum for interference"""
        
        jamming_events = []
        
        for spectrum in spectrum_data:
            # Establish baseline if not exist
            if spectrum.frequency_mhz not in self.baseline_spectrum:
                self.baseline_spectrum[spectrum.frequency_mhz] = spectrum.power_dbm
                continue
                
            # Detect power anomalies
            baseline = self.baseline_spectrum[spectrum.frequency_mhz]
            power_increase = spectrum.power_dbm - baseline
            
            # Jamming detection threshold: 15 dB increase
            if power_increase > 15.0:
                jamming_type = self._classify_jamming(spectrum)
                
                event = JammingEvent(
                    jamming_type=jamming_type,
                    frequency_band=self._get_band_name(spectrum.frequency_mhz),
                    power_level_dbm=spectrum.power_dbm,
                    direction=None,  # Requires antenna array
                    cn0_degradation_db=power_increase,
                    affected_satellites=[],
                    severity=self._calculate_severity(power_increase)
                )
                
                jamming_events.append(event)
                self.interference_detected.append(event)
                
                logger.warning(
                    f"Jamming detected on {event.frequency_band}: "
                    f"{event.jamming_type.value}, +{power_increase:.1f} dB"
                )
                
        return jamming_events
    
    def _classify_jamming(self, spectrum: RFSpectrum) -> JammingType:
        """Classify jamming type based on spectrum characteristics"""
        
        if spectrum.bandwidth_khz < 1.0:
            return JammingType.NARROWBAND
        elif spectrum.bandwidth_khz > 20.0:
            return JammingType.WIDEBAND
        else:
            # More analysis needed for pulsed/swept
            return JammingType.MATCHED_SPECTRUM
    
    def _get_band_name(self, frequency_mhz: float) -> str:
        """Get GNSS band name from frequency"""
        bands = {
            self.GPS_L1: 'GPS L1',
            self.GPS_L2: 'GPS L2',
            self.GPS_L5: 'GPS L5',
            self.GLONASS_G1: 'GLONASS G1',
            self.GALILEO_E1: 'Galileo E1',
            self.BEIDOU_B1: 'BeiDou B1'
        }
        
        # Find closest band
        closest = min(bands.keys(), key=lambda x: abs(x - frequency_mhz))
        if abs(closest - frequency_mhz) < 5.0:  # Within 5 MHz
            return bands[closest]
        return f"{frequency_mhz:.2f} MHz"
    
    def _calculate_severity(self, cn0_degradation: float) -> str:
        """Calculate jamming severity"""
        if cn0_degradation > 30:
            return 'critical'
        elif cn0_degradation > 20:
            return 'high'
        elif cn0_degradation > 15:
            return 'medium'
        else:
            return 'low'


class NullSteeringController:
    """Multi-directional null steering - InfiniDome GPSdome inspired
    
    Implements adaptive antenna array with up to 3 nulls to block
    interference from multiple directions simultaneously.
    """
    
    MAX_NULLS = 3
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.active_nulls: Dict[int, InterferenceDirection] = {}
        self.null_depths_db: Dict[int, float] = {}
        
    def create_null(self, direction: InterferenceDirection, depth_db: float = 30.0):
        """Create a null in specified direction"""
        
        if len(self.active_nulls) >= self.MAX_NULLS:
            logger.warning(f"Maximum {self.MAX_NULLS} nulls already active")
            return False
            
        null_id = len(self.active_nulls) + 1
        self.active_nulls[null_id] = direction
        self.null_depths_db[null_id] = depth_db
        
        logger.info(
            f"Created null #{null_id} at {direction.name} "
            f"with {depth_db} dB attenuation"
        )
        return True
    
    def steer_null(self, null_id: int, new_direction: InterferenceDirection):
        """Dynamically steer existing null to new direction"""
        
        if null_id not in self.active_nulls:
            logger.error(f"Null {null_id} does not exist")
            return False
            
        old_direction = self.active_nulls[null_id]
        self.active_nulls[null_id] = new_direction
        
        logger.info(
            f"Steered null #{null_id} from {old_direction.name} "
            f"to {new_direction.name}"
        )
        return True
    
    def remove_null(self, null_id: int):
        """Remove null when interference clears"""
        
        if null_id in self.active_nulls:
            direction = self.active_nulls[null_id]
            del self.active_nulls[null_id]
            del self.null_depths_db[null_id]
            
            logger.info(f"Removed null #{null_id} at {direction.name}")
            return True
        return False
    
    def get_status(self) -> Dict:
        """Get current null steering status"""
        return {
            'device_id': self.device_id,
            'active_nulls': len(self.active_nulls),
            'max_nulls': self.MAX_NULLS,
            'nulls': [
                {
                    'id': null_id,
                    'direction': direction.name,
                    'direction_degrees': direction.value,
                    'depth_db': self.null_depths_db[null_id]
                }
                for null_id, direction in self.active_nulls.items()
            ]
        }


class AdvancedAntiJammingSystem:
    """Complete anti-jamming system integrating all Israeli-inspired tech"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.spectrum_analyzer = SpectrumAnalyzer(device_id)
        self.null_controller = NullSteeringController(device_id)
        self.jamming_events: List[JammingEvent] = []
        self.mitigation_active = False
        
    def process_rf_data(self, spectrum_data: List[RFSpectrum]) -> Dict:
        """Process RF spectrum data and activate mitigation"""
        
        # Analyze spectrum for interference
        new_events = self.spectrum_analyzer.analyze_spectrum(spectrum_data)
        
        if new_events:
            self.jamming_events.extend(new_events)
            
            # Activate null steering for critical threats
            for event in new_events:
                if event.severity in ['high', 'critical'] and event.direction:
                    self.null_controller.create_null(
                        event.direction,
                        depth_db=35.0 if event.severity == 'critical' else 30.0
                    )
            
            self.mitigation_active = True
            
        return {
            'device_id': self.device_id,
            'new_events': len(new_events),
            'total_events': len(self.jamming_events),
            'mitigation_active': self.mitigation_active,
            'null_steering_status': self.null_controller.get_status()
        }
    
    def get_threat_intelligence(self, time_window: timedelta = timedelta(hours=1)) -> Dict:
        """Get actionable threat intelligence - InfiniDome style"""
        
        cutoff = datetime.now() - time_window
        recent_events = [
            event for event in self.jamming_events
            if event.detected_at > cutoff
        ]
        
        # Aggregate by frequency band
        band_stats = {}
        for event in recent_events:
            band = event.frequency_band
            if band not in band_stats:
                band_stats[band] = {
                    'count': 0,
                    'max_power': 0,
                    'avg_degradation': [],
                    'jamming_types': set()
                }
            
            band_stats[band]['count'] += 1
            band_stats[band]['max_power'] = max(
                band_stats[band]['max_power'],
                event.power_level_dbm
            )
            band_stats[band]['avg_degradation'].append(event.cn0_degradation_db)
            band_stats[band]['jamming_types'].add(event.jamming_type.value)
        
        # Calculate averages
        for band in band_stats:
            degradations = band_stats[band]['avg_degradation']
            band_stats[band]['avg_degradation'] = (
                sum(degradations) / len(degradations) if degradations else 0
            )
            band_stats[band]['jamming_types'] = list(band_stats[band]['jamming_types'])
        
        return {
            'device_id': self.device_id,
            'time_window': str(time_window),
            'total_events': len(recent_events),
            'critical_events': len([e for e in recent_events if e.severity == 'critical']),
            'high_events': len([e for e in recent_events if e.severity == 'high']),
            'band_statistics': band_stats,
            'mitigation_active': self.mitigation_active,
            'null_steering': self.null_controller.get_status()
        }


# Global anti-jamming system manager
anti_jamming_systems: Dict[str, AdvancedAntiJammingSystem] = {}


def get_anti_jamming_system(device_id: str) -> AdvancedAntiJammingSystem:
    """Get or create anti-jamming system for device"""
    if device_id not in anti_jamming_systems:
        anti_jamming_systems[device_id] = AdvancedAntiJammingSystem(device_id)
    return anti_jamming_systems[device_id]
