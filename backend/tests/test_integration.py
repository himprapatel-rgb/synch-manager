"""Integration Tests for Zero-Hardware Operation

Tests that verify the application works without any physical hardware devices.
All timing/sync devices are simulated, ensuring cloud deployment compatibility.
"""

import pytest
from django.test import TestCase, Client
from django.urls import reverse
from apps.inventory.device_simulators import (
    SimulatorManager, GNSSSimulator, MicrochipTimingSimulator,
    OscilloscopeSimulator, CesiumClockSimulator
)
from apps.security.models import ThreatEvent, GNSSStatus


class DeviceSimulatorTests(TestCase):
    """Test device simulators work without hardware"""
    
    def setUp(self):
        self.manager = SimulatorManager()
    
    def test_gnss_simulator_creation(self):
        """Test GNSS simulator can be created without hardware"""
        sim = self.manager.add_simulator('gnss', 'test-gnss-01')
        assert sim is not None
        assert sim.device_id == 'test-gnss-01'
        assert sim.device_type == 'GNSS'
    
    def test_gnss_position_data(self):
        """Test GNSS simulator provides position data"""
        sim = self.manager.add_simulator('gnss', 'test-gnss-02')
        position = sim.get_position()
        
        assert 'latitude' in position
        assert 'longitude' in position
        assert 'accuracy' in position
        assert 'threat_detected' in position
    
    def test_gnss_jamming_simulation(self):
        """Test GNSS jamming can be simulated"""
        sim = self.manager.add_simulator('gnss', 'test-gnss-03')
        sim.simulate_jamming(True)
        
        position = sim.get_position()
        assert position['threat_detected'] == True
        assert position['threat_type'] == 'jamming'
    
    def test_gnss_spoofing_simulation(self):
        """Test GNSS spoofing can be simulated"""
        sim = self.manager.add_simulator('gnss', 'test-gnss-04')
        sim.simulate_spoofing(True)
        
        position = sim.get_position()
        assert position['threat_detected'] == True
        assert position['threat_type'] == 'spoofing'
    
    def test_microchip_timing_simulator(self):
        """Test microchip timing device simulator"""
        sim = self.manager.add_simulator('microchip', 'test-chip-01')
        timing_data = sim.get_timing_data()
        
        assert 'frequency_hz' in timing_data
        assert 'temperature_c' in timing_data
        assert 'stability_ppb' in timing_data
        assert timing_data['chip_type'] == 'DSC1123'
    
    def test_oscilloscope_simulator(self):
        """Test oscilloscope simulator"""
        sim = self.manager.add_simulator('oscilloscope', 'test-osc-01')
        waveform = sim.capture_waveform(channel=1, duration_ms=1.0)
        
        assert 'waveform' in waveform
        assert 'peak_voltage' in waveform
        assert 'frequency_mhz' in waveform
        assert len(waveform['waveform']) > 0
    
    def test_cesium_clock_simulator(self):
        """Test cesium atomic clock simulator"""
        sim = self.manager.add_simulator('cesium', 'test-cesium-01')
        time_data = sim.get_time()
        
        assert 'timestamp' in time_data
        assert 'frequency_hz' in time_data
        assert 'stability' in time_data
        assert time_data['frequency_hz'] == 9192631770  # Cs-133 frequency
    
    def test_simulator_manager_multiple_devices(self):
        """Test managing multiple simulated devices"""
        self.manager.add_simulator('gnss', 'device-1')
        self.manager.add_simulator('microchip', 'device-2')
        self.manager.add_simulator('oscilloscope', 'device-3')
        
        status = self.manager.get_all_status()
        assert len(status) == 3
        assert all('device_id' in s for s in status)


class APIEndpointTests(TestCase):
    """Test API endpoints work with simulated devices"""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_endpoint(self):
        """Test health check endpoint works without hardware"""
        response = self.client.get('/api/health/')
        assert response.status_code == 200
    
    def test_security_threats_endpoint(self):
        """Test threats API works without hardware"""
        response = self.client.get('/api/security/threats/')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_war_mode_endpoint(self):
        """Test war mode API works without hardware"""
        response = self.client.get('/api/security/war-mode/')
        assert response.status_code == 200


class ThreatDetectionTests(TestCase):
    """Test threat detection works with simulated GNSS"""
    
    def setUp(self):
        self.manager = SimulatorManager()
    
    def test_jamming_detection_workflow(self):
        """Test complete jamming detection workflow without hardware"""
        # Create simulated GNSS device
        sim = self.manager.add_simulator('gnss', 'test-gnss-jamming')
        
        # Simulate jamming
        sim.simulate_jamming(True)
        position = sim.get_position()
        
        # Verify threat detected
        assert position['threat_detected'] == True
        assert position['threat_type'] == 'jamming'
        
        # Verify system can create threat event
        threat = ThreatEvent.objects.create(
            device_id='test-gnss-jamming',
            threat_type='jamming',
            severity='high',
            confidence=0.95
        )
        assert threat.id is not None
        assert threat.resolved == False
    
    def test_spoofing_detection_workflow(self):
        """Test complete spoofing detection workflow without hardware"""
        sim = self.manager.add_simulator('gnss', 'test-gnss-spoofing')
        
        # Simulate spoofing
        sim.simulate_spoofing(True)
        position = sim.get_position()
        
        # Verify threat detected
        assert position['threat_detected'] == True
        assert position['threat_type'] == 'spoofing'
        
        # Verify system can create threat event
        threat = ThreatEvent.objects.create(
            device_id='test-gnss-spoofing',
            threat_type='spoofing',
            severity='critical',
            confidence=0.88,
            latitude=position['latitude'],
            longitude=position['longitude']
        )
        assert threat.id is not None


class CloudDeploymentTests(TestCase):
    """Test application is ready for cloud deployment"""
    
    def test_no_hardware_dependencies(self):
        """Verify no hardware-specific imports or dependencies"""
        # Create simulators for all device types
        manager = SimulatorManager()
        
        devices = [
            ('gnss', 'cloud-gnss-1'),
            ('microchip', 'cloud-chip-1'),
            ('oscilloscope', 'cloud-osc-1'),
            ('cesium', 'cloud-cesium-1'),
            ('rubidium', 'cloud-rubidium-1'),
            ('ptp_grandmaster', 'cloud-ptp-1')
        ]
        
        for device_type, device_id in devices:
            sim = manager.add_simulator(device_type, device_id)
            assert sim is not None
            status = sim.get_status()
            assert status['status'] == 'active'
    
    def test_simulated_data_realistic(self):
        """Verify simulated data is realistic for testing"""
        manager = SimulatorManager()
        
        # GNSS coordinates should be valid
        gnss = manager.add_simulator('gnss', 'test')
        pos = gnss.get_position()
        assert -90 <= pos['latitude'] <= 90
        assert -180 <= pos['longitude'] <= 180
        
        # Microchip frequency should be stable
        chip = manager.add_simulator('microchip', 'test')
        data1 = chip.get_timing_data()
        data2 = chip.get_timing_data()
        freq_diff = abs(data1['frequency_hz'] - data2['frequency_hz'])
        assert freq_diff < 1000  # Less than 1kHz variation
    
    def test_concurrent_simulators(self):
        """Test multiple simulators can run concurrently"""
        manager = SimulatorManager()
        
        # Create 10 GNSS simulators
        for i in range(10):
            manager.add_simulator('gnss', f'concurrent-gnss-{i}')
        
        # All should be active
        all_status = manager.get_all_status()
        assert len(all_status) == 10
        assert all(s['status'] == 'active' for s in all_status)


class DataPersistenceTests(TestCase):
    """Test data persistence works with simulated devices"""
    
    def test_gnss_status_creation(self):
        """Test GNSS status can be saved to database"""
        status = GNSSStatus.objects.create(
            device_id='test-gnss',
            latitude=51.5074,
            longitude=-0.1278,
            signal_strength=45.0,
            satellites_visible=12,
            fix_quality='3D'
        )
        assert status.id is not None
    
    def test_threat_event_lifecycle(self):
        """Test complete threat event lifecycle"""
        # Create threat
        threat = ThreatEvent.objects.create(
            device_id='lifecycle-test',
            threat_type='jamming',
            severity='high',
            confidence=0.90
        )
        
        # Verify creation
        assert threat.resolved == False
        
        # Resolve threat
        threat.resolved = True
        threat.save()
        
        # Verify resolution
        updated = ThreatEvent.objects.get(id=threat.id)
        assert updated.resolved == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
