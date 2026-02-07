"""War Mode Tactical Timing Module

Military-grade timing resilience for extreme scenarios including:
- GNSS denial environments
- Electronic warfare conditions
- Contested operational environments
- Multi-domain operations (MDO)
- Tactical edge computing scenarios
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class WarModeLevel(Enum):
    """War mode readiness levels"""
    PEACETIME = 'peacetime'  # Normal operations
    ELEVATED = 'elevated'    # Increased threat awareness
    TACTICAL = 'tactical'    # Active threat environment
    CRITICAL = 'critical'    # GNSS denied, contested environment
    HOLDOVER = 'holdover'    # All external sources lost


class ThreatEnvironment(Enum):
    """Operational threat environments"""
    BENIGN = 'benign'
    JAMMING = 'jamming'
    SPOOFING = 'spoofing'
    KINETIC = 'kinetic'  # Physical attack
    CYBER = 'cyber'
    EMP = 'emp'  # Electromagnetic pulse
    MULTI_DOMAIN = 'multi_domain'  # Combined threats


class TimingSource(Enum):
    """Available timing sources in priority order"""
    GNSS_PRIMARY = ('gnss_primary', 1)
    GNSS_SECONDARY = ('gnss_secondary', 2)
    LEO_PNT = ('leo_pnt', 3)  # Starlink, OneWeb, Iridium
    ELORAN = ('eloran', 4)
    WHITE_RABBIT = ('white_rabbit', 5)
    CSAC = ('csac', 6)  # Chip-Scale Atomic Clock
    OCXO = ('ocxo', 7)  # Oven-Controlled Crystal Oscillator
    RUBIDIUM = ('rubidium', 8)
    CESIUM = ('cesium', 9)  # Ultimate backup (Cesium PRS-4400)
    HOLDOVER = ('holdover', 10)
    
    def __init__(self, source_name, priority):
        self.source_name = source_name
        self.priority = priority


class HoldoverQuality(Enum):
    """Holdover quality classifications"""
    EXCELLENT = 'excellent'  # < 1us/day
    GOOD = 'good'           # < 10us/day
    ACCEPTABLE = 'acceptable'  # < 100us/day
    DEGRADED = 'degraded'   # < 1ms/day
    POOR = 'poor'           # > 1ms/day


class TacticalTimingController:
    """Controls timing source selection in tactical environments"""
    
    # Holdover thresholds (seconds per day)
    HOLDOVER_THRESHOLDS = {
        HoldoverQuality.EXCELLENT: 1e-6,
        HoldoverQuality.GOOD: 10e-6,
        HoldoverQuality.ACCEPTABLE: 100e-6,
        HoldoverQuality.DEGRADED: 1e-3,
        HoldoverQuality.POOR: float('inf')
    }
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.current_mode = WarModeLevel.PEACETIME
        self.threat_environment = ThreatEnvironment.BENIGN
        self.active_source = TimingSource.GNSS_PRIMARY
        self.available_sources: Dict[TimingSource, bool] = {}
        self.holdover_started: Optional[datetime] = None
        self.holdover_quality = HoldoverQuality.EXCELLENT
        self.mode_history: List[Dict] = []
        self.source_quality: Dict[TimingSource, float] = {}
        
    def assess_war_mode(self, threat_indicators: Dict) -> WarModeLevel:
        """Assess appropriate war mode level based on threat indicators"""
        
        gnss_available = threat_indicators.get('gnss_available', True)
        cn0_level = threat_indicators.get('cn0_db_hz', 45.0)
        peer_divergence = threat_indicators.get('peer_divergence', 0.0)
        jamming_detected = threat_indicators.get('jamming_detected', False)
        spoofing_detected = threat_indicators.get('spoofing_detected', False)
        
        # Determine war mode level
        if spoofing_detected or peer_divergence > 1e-3:  # > 1ms divergence
            new_mode = WarModeLevel.CRITICAL
        elif jamming_detected or cn0_level < 30.0:
            new_mode = WarModeLevel.TACTICAL
        elif not gnss_available or cn0_level < 35.0:
            new_mode = WarModeLevel.ELEVATED
        else:
            new_mode = WarModeLevel.PEACETIME
        
        # Log mode changes
        if new_mode != self.current_mode:
            self.mode_history.append({
                'timestamp': datetime.now(),
                'from_mode': self.current_mode.value,
                'to_mode': new_mode.value,
                'threat_indicators': threat_indicators
            })
            
            logger.warning(
                f"War mode transition: {self.current_mode.value} -> {new_mode.value}"
            )
            
            self.current_mode = new_mode
        
        return new_mode
    
    def select_optimal_source(self, mode: WarModeLevel) -> TimingSource:
        """Select optimal timing source based on war mode"""
        
        # Get available sources sorted by priority
        available = sorted(
            [src for src, avail in self.available_sources.items() if avail],
            key=lambda x: x.priority
        )
        
        if not available:
            logger.critical("No timing sources available - entering holdover")
            return self._enter_holdover()
        
        # Mode-specific source selection logic
        if mode == WarModeLevel.PEACETIME:
            # Prefer GNSS in peacetime
            preferred = [TimingSource.GNSS_PRIMARY, TimingSource.GNSS_SECONDARY]
        
        elif mode == WarModeLevel.ELEVATED:
            # Diversify sources
            preferred = [
                TimingSource.GNSS_PRIMARY,
                TimingSource.LEO_PNT,
                TimingSource.GNSS_SECONDARY
            ]
        
        elif mode == WarModeLevel.TACTICAL:
            # Avoid GNSS if degraded
            preferred = [
                TimingSource.LEO_PNT,
                TimingSource.ELORAN,
                TimingSource.CSAC,
                TimingSource.WHITE_RABBIT
            ]
        
        elif mode == WarModeLevel.CRITICAL:
            # Use only hardened sources
            preferred = [
                TimingSource.CSAC,
                TimingSource.CESIUM,
                TimingSource.RUBIDIUM,
                TimingSource.ELORAN
            ]
        
        else:  # HOLDOVER
            return self._enter_holdover()
        
        # Select first available preferred source
        for source in preferred:
            if source in available:
                if source != self.active_source:
                    logger.info(f"Switching to {source.source_name}")
                    self.active_source = source
                return source
        
        # Fallback to any available source
        self.active_source = available[0]
        return available[0]
    
    def _enter_holdover(self) -> TimingSource:
        """Enter holdover mode"""
        if self.holdover_started is None:
            self.holdover_started = datetime.now()
            logger.critical("Entering HOLDOVER mode - no external timing sources")
        
        self.active_source = TimingSource.HOLDOVER
        return TimingSource.HOLDOVER
    
    def calculate_holdover_quality(self, elapsed_time: timedelta, 
                                   drift_rate: float) -> HoldoverQuality:
        """Calculate current holdover quality"""
        
        # drift_rate in seconds per second
        total_drift = drift_rate * elapsed_time.total_seconds()
        
        for quality, threshold in self.HOLDOVER_THRESHOLDS.items():
            if abs(total_drift) < threshold:
                self.holdover_quality = quality
                return quality
        
        return HoldoverQuality.POOR
    
    def get_tactical_status(self) -> Dict:
        """Get comprehensive tactical timing status"""
        
        holdover_duration = None
        if self.holdover_started:
            holdover_duration = (datetime.now() - self.holdover_started).total_seconds()
        
        return {
            'device_id': self.device_id,
            'war_mode': self.current_mode.value,
            'threat_environment': self.threat_environment.value,
            'active_source': self.active_source.source_name,
            'available_sources': [
                src.source_name for src, avail in self.available_sources.items() if avail
            ],
            'holdover_duration_seconds': holdover_duration,
            'holdover_quality': self.holdover_quality.value if holdover_duration else None,
            'mode_transitions': len(self.mode_history),
            'timestamp': datetime.now().isoformat()
        }


class MultiDomainTiming:
    """Coordinates timing across multi-domain operations"""
    
    def __init__(self):
        self.controllers: Dict[str, TacticalTimingController] = {}
        self.domain_timing_quality: Dict[str, float] = {}
        self.sync_mesh_active = False
        
    def register_controller(self, domain: str, device_id: str) -> TacticalTimingController:
        """Register timing controller for operational domain"""
        controller = TacticalTimingController(device_id)
        self.controllers[f"{domain}:{device_id}"] = controller
        return controller
    
    def coordinate_tactical_timing(self, threat_level: str) -> Dict:
        """Coordinate timing across all domains"""
        
        domain_statuses = {}
        for domain_device, controller in self.controllers.items():
            status = controller.get_tactical_status()
            domain_statuses[domain_device] = status
        
        # Assess overall tactical timing health
        critical_count = sum(
            1 for status in domain_statuses.values()
            if status['war_mode'] in ['critical', 'holdover']
        )
        
        overall_health = 'degraded' if critical_count > len(self.controllers) / 2 else 'operational'
        
        return {
            'overall_health': overall_health,
            'domains': domain_statuses,
            'critical_domains': critical_count,
            'sync_mesh_active': self.sync_mesh_active,
            'timestamp': datetime.now().isoformat()
        }
    
    def enable_sync_mesh(self):
        """Enable peer-to-peer timing synchronization mesh"""
        self.sync_mesh_active = True
        logger.info("Tactical timing mesh network activated")
    
    def disable_sync_mesh(self):
        """Disable timing mesh (EMCON - emissions control)"""
        self.sync_mesh_active = False
        logger.info("Tactical timing mesh deactivated (EMCON)")


class CSACManager:
    """Manages Chip-Scale Atomic Clock for tactical holdover"""
    
    # CSAC specifications (based on SA.45s CSAC)
    CSAC_ALLAN_DEVIATION = 2e-10  # @ 1 second
    CSAC_DRIFT_RATE = 5e-11  # per day typical
    CSAC_WARMUP_TIME = 180  # seconds
    
    def __init__(self):
        self.is_active = False
        self.activation_time: Optional[datetime] = None
        self.temperature: float = 25.0
        self.power_consumption: float = 0.12  # Watts
        
    def activate(self):
        """Activate CSAC"""
        self.is_active = True
        self.activation_time = datetime.now()
        logger.info(f"CSAC activated - warmup time: {self.CSAC_WARMUP_TIME}s")
    
    def is_ready(self) -> bool:
        """Check if CSAC is warmed up and ready"""
        if not self.is_active or self.activation_time is None:
            return False
        
        elapsed = (datetime.now() - self.activation_time).total_seconds()
        return elapsed >= self.CSAC_WARMUP_TIME
    
    def get_expected_drift(self, duration: timedelta) -> float:
        """Calculate expected CSAC drift over duration"""
        days = duration.total_seconds() / 86400
        return self.CSAC_DRIFT_RATE * days
    
    def get_status(self) -> Dict:
        """Get CSAC status"""
        ready = self.is_ready()
        
        return {
            'active': self.is_active,
            'ready': ready,
            'temperature_c': self.temperature,
            'power_watts': self.power_consumption if self.is_active else 0.0,
            'allan_deviation': self.CSAC_ALLAN_DEVIATION,
            'drift_rate_per_day': self.CSAC_DRIFT_RATE
        }


# Global tactical timing coordinator
tactical_coordinator = MultiDomainTiming()
