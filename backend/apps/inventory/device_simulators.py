"""Device Simulators - Zero Hardware Dependency

Simulates all timing/sync devices without physical hardware:
- GNSS receivers (with jamming/spoofing simulation)
- Microchip timing devices
- Oscilloscopes
- Network time protocol devices
- Cesium atomic clocks
- Rubidium frequency standards
- PTP grandmaster clocks
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np


class BaseDeviceSimulator:
    """Base class for all device simulators"""
    
    def __init__(self, device_id: str, device_type: str):
        self.device_id = device_id
        self.device_type = device_type
        self.status = "active"
        self.start_time = datetime.now()
        self.error_rate = 0.0
    
    def get_status(self) -> Dict:
        return {
            'device_id': self.device_id,
            'type': self.device_type,
            'status': self.status,
            'uptime': str(datetime.now() - self.start_time),
            'error_rate': self.error_rate
        }


class GNSSSimulator(BaseDeviceSimulator):
    """Simulates GNSS receivers with threat scenarios"""
    
    def __init__(self, device_id: str):
        super().__init__(device_id, "GNSS")
        self.latitude = 51.5074  # London default
        self.longitude = -0.1278
        self.satellites = []
        self.jamming_active = False
        self.spoofing_active = False
        self.signal_strength = 45.0  # dBHz
        
    def get_position(self) -> Dict:
        """Get current position with potential threats"""
        if self.spoofing_active:
            # Simulate spoofed position
            return {
                'latitude': self.latitude + random.uniform(-0.1, 0.1),
                'longitude': self.longitude + random.uniform(-0.1, 0.1),
                'accuracy': random.uniform(50, 500),
                'threat_detected': True,
                'threat_type': 'spoofing'
            }
        
        if self.jamming_active:
            return {
                'latitude': None,
                'longitude': None,
                'accuracy': None,
                'threat_detected': True,
                'threat_type': 'jamming',
                'signal_strength': self.signal_strength * 0.1
            }
        
        return {
            'latitude': self.latitude + random.uniform(-0.00001, 0.00001),
            'longitude': self.longitude + random.uniform(-0.00001, 0.00001),
            'accuracy': random.uniform(1, 5),
            'threat_detected': False,
            'signal_strength': self.signal_strength
        }
    
    def simulate_jamming(self, active: bool = True):
        """Enable/disable jamming simulation"""
        self.jamming_active = active
        if active:
            self.signal_strength = random.uniform(10, 20)
        else:
            self.signal_strength = random.uniform(40, 50)
    
    def simulate_spoofing(self, active: bool = True):
        """Enable/disable spoofing simulation"""
        self.spoofing_active = active
    
    def get_satellites(self) -> List[Dict]:
        """Get visible satellite data"""
        if self.jamming_active:
            return []
        
        num_sats = 4 if self.spoofing_active else random.randint(8, 12)
        return [
            {
                'prn': i + 1,
                'elevation': random.uniform(5, 90),
                'azimuth': random.uniform(0, 360),
                'snr': random.uniform(30, 50) if not self.spoofing_active else random.uniform(45, 55)
            }
            for i in range(num_sats)
        ]


class MicrochipTimingSimulator(BaseDeviceSimulator):
    """Simulates microchip timing devices"""
    
    def __init__(self, device_id: str, chip_type: str = "DSC1123"):
        super().__init__(device_id, f"Microchip-{chip_type}")
        self.chip_type = chip_type
        self.frequency = 10000000  # 10 MHz default
        self.temperature = 25.0  # Celsius
        self.stability = 1e-9  # parts per billion
    
    def get_timing_data(self) -> Dict:
        """Get current timing measurements"""
        # Simulate frequency drift with temperature
        temp_drift = (self.temperature - 25.0) * 0.5e-9
        actual_freq = self.frequency * (1 + self.stability + temp_drift + random.uniform(-1e-10, 1e-10))
        
        return {
            'device_id': self.device_id,
            'chip_type': self.chip_type,
            'frequency_hz': actual_freq,
            'temperature_c': self.temperature + random.uniform(-0.5, 0.5),
            'stability_ppb': self.stability * 1e9,
            'timestamp': datetime.now().isoformat()
        }
    
    def set_temperature(self, temp: float):
        """Simulate temperature change"""
        self.temperature = temp


class OscilloscopeSimulator(BaseDeviceSimulator):
    """Simulates oscilloscope measurements"""
    
    def __init__(self, device_id: str, model: str = "Generic-OSC"):
        super().__init__(device_id, f"Oscilloscope-{model}")
        self.model = model
        self.sample_rate = 1e9  # 1 GSa/s
        self.bandwidth = 500e6  # 500 MHz
        self.channels = 4
    
    def capture_waveform(self, channel: int = 1, duration_ms: float = 1.0) -> Dict:
        """Simulate waveform capture"""
        samples = int(self.sample_rate * duration_ms / 1000)
        time_axis = np.linspace(0, duration_ms, min(samples, 10000))
        
        # Simulate 10 MHz sine wave with noise
        frequency = 10e6
        waveform = np.sin(2 * np.pi * frequency * time_axis / 1000) + np.random.normal(0, 0.1, len(time_axis))
        
        return {
            'device_id': self.device_id,
            'channel': channel,
            'sample_rate': self.sample_rate,
            'duration_ms': duration_ms,
            'waveform': waveform.tolist()[:100],  # First 100 samples
            'peak_voltage': float(np.max(waveform)),
            'frequency_mhz': frequency / 1e6,
            'timestamp': datetime.now().isoformat()
        }


class CesiumClockSimulator(BaseDeviceSimulator):
    """Simulates cesium atomic clock"""
    
    def __init__(self, device_id: str):
        super().__init__(device_id, "Cesium-Atomic-Clock")
        self.frequency = 9192631770  # Cesium-133 transition frequency
        self.stability = 1e-13  # Ultra-stable
        self.drift_rate = 1e-14
    
    def get_time(self) -> Dict:
        """Get ultra-precise time"""
        return {
            'device_id': self.device_id,
            'timestamp': datetime.now().isoformat(),
            'frequency_hz': self.frequency,
            'stability': self.stability,
            'drift_rate': self.drift_rate,
            'accuracy_ns': random.uniform(0.1, 1.0)
        }


class RubidiumClockSimulator(BaseDeviceSimulator):
    """Simulates rubidium frequency standard"""
    
    def __init__(self, device_id: str):
        super().__init__(device_id, "Rubidium-Clock")
        self.frequency = 10000000  # 10 MHz output
        self.stability = 1e-11
    
    def get_frequency(self) -> Dict:
        """Get frequency output"""
        actual_freq = self.frequency * (1 + random.uniform(-self.stability, self.stability))
        return {
            'device_id': self.device_id,
            'frequency_hz': actual_freq,
            'stability': self.stability,
            'timestamp': datetime.now().isoformat()
        }


class PTPGrandmasterSimulator(BaseDeviceSimulator):
    """Simulates PTP Grandmaster clock"""
    
    def __init__(self, device_id: str):
        super().__init__(device_id, "PTP-Grandmaster")
        self.clock_class = 6  # Primary reference
        self.accuracy = 25  # nanoseconds
        self.priority1 = 128
        self.priority2 = 128
    
    def get_ptp_status(self) -> Dict:
        """Get PTP status"""
        return {
            'device_id': self.device_id,
            'clock_class': self.clock_class,
            'clock_accuracy': self.accuracy,
            'offset_scaled_log_variance': 4800,
            'priority1': self.priority1,
            'priority2': self.priority2,
            'grandmaster_identity': self.device_id,
            'steps_removed': 0,
            'time_source': 'GPS',
            'timestamp': datetime.now().isoformat()
        }


class DeviceSimulatorFactory:
    """Factory to create device simulators"""
    
    @staticmethod
    def create_simulator(device_type: str, device_id: str, **kwargs) -> BaseDeviceSimulator:
        """Create appropriate simulator based on device type"""
        simulators = {
            'gnss': GNSSSimulator,
            'microchip': MicrochipTimingSimulator,
            'oscilloscope': OscilloscopeSimulator,
            'cesium': CesiumClockSimulator,
            'rubidium': RubidiumClockSimulator,
            'ptp_grandmaster': PTPGrandmasterSimulator
        }
        
        simulator_class = simulators.get(device_type.lower())
        if not simulator_class:
            raise ValueError(f"Unknown device type: {device_type}")
        
        return simulator_class(device_id, **kwargs)


class SimulatorManager:
    """Manages all device simulators"""
    
    def __init__(self):
        self.simulators: Dict[str, BaseDeviceSimulator] = {}
    
    def add_simulator(self, device_type: str, device_id: str, **kwargs) -> BaseDeviceSimulator:
        """Add new simulator"""
        simulator = DeviceSimulatorFactory.create_simulator(device_type, device_id, **kwargs)
        self.simulators[device_id] = simulator
        return simulator
    
    def get_simulator(self, device_id: str) -> Optional[BaseDeviceSimulator]:
        """Get simulator by ID"""
        return self.simulators.get(device_id)
    
    def remove_simulator(self, device_id: str):
        """Remove simulator"""
        if device_id in self.simulators:
            del self.simulators[device_id]
    
    def get_all_status(self) -> List[Dict]:
        """Get status of all simulators"""
        return [sim.get_status() for sim in self.simulators.values()]


# Global simulator manager instance
simulator_manager = SimulatorManager()
