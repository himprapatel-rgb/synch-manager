"""OSNMA (Open Service Navigation Message Authentication) - Anti-Spoofing

Implements Galileo OSNMA cryptographic authentication inspired by:
- Septentrio AIM+ (signal diversity + cryptography + heuristics)
- Galileo OSNMA specification (ECDSA P-256/P-521, HMAC-SHA-256)

Provides cryptographic verification of GNSS navigation messages
to detect and mitigate spoofing attacks.
"""

import logging
import hashlib
import hmac
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class AuthenticationStatus(Enum):
    """OSNMA authentication result status"""
    AUTHENTICATED = 'authenticated'
    FAILED = 'failed'
    PENDING = 'pending'
    UNAVAILABLE = 'unavailable'


class SpoofingIndicator(Enum):
    """Spoofing detection indicators"""
    POWER_ANOMALY = 'power_anomaly'
    SIGNAL_STRUCTURE = 'signal_structure'
    CRYPTO_FAILURE = 'crypto_failure'
    TIME_INCONSISTENCY = 'time_inconsistency'
    DOPPLER_ANOMALY = 'doppler_anomaly'
    CODE_CARRIER_DIVERGENCE = 'code_carrier_divergence'


@dataclass
class OSNMAMessage:
    """OSNMA navigation message data"""
    satellite_id: int
    message_type: str
    timestamp: datetime
    data: bytes
    signature: Optional[bytes] = None
    public_key: Optional[bytes] = None
    authenticated: AuthenticationStatus = AuthenticationStatus.PENDING


class OSNMAAuthenticator:
    """Cryptographic authenticator for Galileo OSNMA - Septentrio AIM+ inspired"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.public_keys: Dict[int, bytes] = {}  # satellite_id -> public_key
        self.authentication_history: List[Dict] = []
        self.spoofing_events: List[Dict] = []
        
    def verify_message(self, message: OSNMAMessage) -> bool:
        """Verify OSNMA message using cryptographic signature"""
        
        if not message.signature or not message.public_key:
            message.authenticated = AuthenticationStatus.UNAVAILABLE
            return False
            
        try:
            # HMAC-SHA-256 verification (simplified - real OSNMA uses ECDSA)
            expected_mac = hmac.new(
                message.public_key,
                message.data,
                hashlib.sha256
            ).digest()
            
            if hmac.compare_digest(expected_mac, message.signature):
                message.authenticated = AuthenticationStatus.AUTHENTICATED
                
                self.authentication_history.append({
                    'satellite_id': message.satellite_id,
                    'timestamp': message.timestamp,
                    'status': 'authenticated'
                })
                
                logger.info(
                    f"OSNMA authenticated: SV{message.satellite_id} "
                    f"at {message.timestamp}"
                )
                return True
            else:
                message.authenticated = AuthenticationStatus.FAILED
                
                # Crypto failure = possible spoofing
                self._log_spoofing_event(
                    message.satellite_id,
                    SpoofingIndicator.CRYPTO_FAILURE,
                    f"OSNMA authentication failed for SV{message.satellite_id}"
                )
                
                logger.error(
                    f"OSNMA FAILED: SV{message.satellite_id} - "
                    f"Possible spoofing attack!"
                )
                return False
                
        except Exception as e:
            logger.error(f"OSNMA verification error: {e}")
            message.authenticated = AuthenticationStatus.FAILED
            return False
    
    def _log_spoofing_event(self, satellite_id: int, indicator: SpoofingIndicator, details: str):
        """Log potential spoofing event"""
        event = {
            'device_id': self.device_id,
            'satellite_id': satellite_id,
            'indicator': indicator.value,
            'details': details,
            'timestamp': datetime.now()
        }
        self.spoofing_events.append(event)
        
    def get_authentication_rate(self, time_window: timedelta = timedelta(minutes=5)) -> float:
        """Get OSNMA authentication success rate"""
        cutoff = datetime.now() - time_window
        recent = [
            h for h in self.authentication_history
            if h['timestamp'] > cutoff
        ]
        
        if not recent:
            return 0.0
            
        authenticated = len([h for h in recent if h['status'] == 'authenticated'])
        return (authenticated / len(recent)) * 100.0


class HeuristicSpoofingDetector:
    """Heuristic-based spoofing detection - Septentrio AIM+ multi-layer approach"""
    
    # Detection thresholds
    POWER_JUMP_THRESHOLD = 6.0  # dB
    DOPPLER_ANOMALY_THRESHOLD = 5.0  # Hz
    CODE_CARRIER_THRESHOLD = 0.1  # meters
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.baseline_power: Dict[int, float] = {}  # satellite_id -> power
        self.baseline_doppler: Dict[int, float] = {}
        self.detections: List[Dict] = []
        
    def detect_power_anomaly(self, satellite_id: int, power_dbm: float) -> Optional[Dict]:
        """Detect sudden power increase (spoofing signature)"""
        
        if satellite_id in self.baseline_power:
            power_jump = power_dbm - self.baseline_power[satellite_id]
            
            if power_jump > self.POWER_JUMP_THRESHOLD:
                detection = {
                    'indicator': SpoofingIndicator.POWER_ANOMALY,
                    'satellite_id': satellite_id,
                    'power_jump_db': power_jump,
                    'timestamp': datetime.now()
                }
                self.detections.append(detection)
                
                logger.warning(
                    f"Power anomaly detected on SV{satellite_id}: "
                    f"+{power_jump:.1f} dB"
                )
                return detection
                
        self.baseline_power[satellite_id] = power_dbm
        return None
    
    def detect_code_carrier_divergence(self, satellite_id: int, 
                                       code_phase: float, 
                                       carrier_phase: float) -> Optional[Dict]:
        """Detect code-carrier divergence (spoofing signature)"""
        
        # Code and carrier should track closely
        divergence = abs(code_phase - carrier_phase)
        
        if divergence > self.CODE_CARRIER_THRESHOLD:
            detection = {
                'indicator': SpoofingIndicator.CODE_CARRIER_DIVERGENCE,
                'satellite_id': satellite_id,
                'divergence_m': divergence,
                'timestamp': datetime.now()
            }
            self.detections.append(detection)
            
            logger.warning(
                f"Code-carrier divergence on SV{satellite_id}: "
                f"{divergence:.3f} m"
            )
            return detection
            
        return None
    
    def get_spoofing_score(self, time_window: timedelta = timedelta(minutes=5)) -> int:
        """Calculate spoofing likelihood score (0-100)"""
        cutoff = datetime.now() - time_window
        recent_detections = [
            d for d in self.detections
            if d['timestamp'] > cutoff
        ]
        
        # Score based on number and severity of indicators
        score = min(len(recent_detections) * 20, 100)
        return score


class ComprehensiveAntiSpoofingSystem:
    """Complete anti-spoofing system integrating cryptographic + heuristic methods"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.osnma_auth = OSNMAAuthenticator(device_id)
        self.heuristic_detector = HeuristicSpoofingDetector(device_id)
        self.spoofing_detected = False
        
    def analyze_signal(self, satellite_id: int, power_dbm: float, 
                      code_phase: float, carrier_phase: float,
                      osnma_message: Optional[OSNMAMessage] = None) -> Dict:
        """Comprehensive spoofing analysis using all detection methods"""
        
        threats = []
        
        # 1. Cryptographic verification (if OSNMA available)
        if osnma_message:
            if not self.osnma_auth.verify_message(osnma_message):
                threats.append('OSNMA_FAILURE')
        
        # 2. Heuristic detections
        if self.heuristic_detector.detect_power_anomaly(satellite_id, power_dbm):
            threats.append('POWER_ANOMALY')
            
        if self.heuristic_detector.detect_code_carrier_divergence(
            satellite_id, code_phase, carrier_phase
        ):
            threats.append('CODE_CARRIER_DIVERGENCE')
        
        # 3. Calculate overall spoofing probability
        spoofing_score = self.heuristic_detector.get_spoofing_score()
        osnma_rate = self.osnma_auth.get_authentication_rate()
        
        # Combined assessment
        if spoofing_score > 60 or (threats and osnma_rate < 50):
            self.spoofing_detected = True
        else:
            self.spoofing_detected = False
        
        return {
            'device_id': self.device_id,
            'satellite_id': satellite_id,
            'spoofing_detected': self.spoofing_detected,
            'spoofing_score': spoofing_score,
            'osnma_auth_rate': osnma_rate,
            'threats': threats,
            'timestamp': datetime.now()
        }


# Global anti-spoofing systems
anti_spoofing_systems: Dict[str, ComprehensiveAntiSpoofingSystem] = {}


def get_anti_spoofing_system(device_id: str) -> ComprehensiveAntiSpoofingSystem:
    """Get or create anti-spoofing system for device"""
    if device_id not in anti_spoofing_systems:
        anti_spoofing_systems[device_id] = ComprehensiveAntiSpoofingSystem(device_id)
    return anti_spoofing_systems[device_id]
