"""NTG (National Timing Grid) App Models - Inspired by NTG.ie

Features:
- Common View Time Transfer (CVTT) for atomic clock comparison
- NTG measurement nodes for GNSS timing
- Real-time clock stability tracking with early warnings
- Jamming detection and spectrum monitoring
- Spoofing detection (multiple algorithms)
- UTC traceability through national standards
- Atomic clock interlink grid for resilience
- PTP link stability evaluation using CVTT
- Multi-GNSS support (GPS, Galileo, BeiDou, GLONASS)
- Holdover management during GNSS degradation
"""
from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid


class NTGNode(models.Model):
    """NTG measurement node - core hardware for timing grid"""
    NODE_STATUS = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('degraded', 'Degraded'),
        ('maintenance', 'Maintenance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    altitude_m = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=NODE_STATUS, default='offline')
    
    # Hardware configuration
    gnss_receiver_model = models.CharField(max_length=100)
    gnss_antenna_model = models.CharField(max_length=100)
    firmware_version = models.CharField(max_length=50)
    
    # Input signal configuration
    input_1pps_enabled = models.BooleanField(default=True)
    input_10mhz_enabled = models.BooleanField(default=False)
    
    # Multi-GNSS constellation support
    gps_enabled = models.BooleanField(default=True)
    galileo_enabled = models.BooleanField(default=True)
    glonass_enabled = models.BooleanField(default=True)
    beidou_enabled = models.BooleanField(default=True)
    
    # Security features
    jamming_detection_enabled = models.BooleanField(default=True)
    spoofing_detection_enabled = models.BooleanField(default=True)
    spectrum_monitoring_enabled = models.BooleanField(default=True)
    
    # Connection to atomic clock
    connected_atomic_clock = models.ForeignKey(
        'AtomicClock', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ntg_nodes'
    )
    
    installed_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ntg_nodes'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.location})"


class AtomicClock(models.Model):
    """Atomic clock for the National Timing Grid"""
    CLOCK_TYPES = [
        ('cesium', 'Cesium'),
        ('rubidium', 'Rubidium'),
        ('hydrogen_maser', 'Hydrogen Maser'),
        ('chip_scale', 'Chip Scale Atomic Clock (CSAC)'),
    ]
    
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('degraded', 'Degraded'),
        ('holdover', 'Holdover Mode'),
        ('offline', 'Offline'),
        ('calibrating', 'Calibrating'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    clock_type = models.CharField(max_length=30, choices=CLOCK_TYPES)
    manufacturer = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    
    # Location and ownership
    organization = models.CharField(max_length=200)
    location = models.CharField(max_length=255)
    
    # Performance specifications
    frequency_stability_1s = models.FloatField(help_text='Allan deviation at 1s')
    frequency_stability_1day = models.FloatField(help_text='Allan deviation at 1 day')
    accuracy_ppb = models.FloatField(help_text='Accuracy in parts per billion')
    
    # UTC traceability
    utc_traceable = models.BooleanField(default=False)
    utc_reference = models.CharField(max_length=50, blank=True, help_text='e.g., UTC(NSAI), UTC(NIST)')
    utc_offset_ns = models.FloatField(default=0, help_text='Current offset from UTC in nanoseconds')
    
    # Holdover capability
    holdover_drift_ns_per_day = models.FloatField(help_text='Expected drift during GNSS outage')
    max_holdover_days = models.IntegerField(default=14)
    
    installed_at = models.DateTimeField(auto_now_add=True)
    last_calibration = models.DateTimeField(null=True, blank=True)
    next_calibration_due = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ntg_atomic_clocks'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_clock_type_display()})"


class CommonViewTimeTransfer(models.Model):
    """CVTT measurement between two NTG nodes/atomic clocks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    
    # Nodes involved in comparison
    node_a = models.ForeignKey(NTGNode, on_delete=models.CASCADE, related_name='cvtt_as_node_a')
    node_b = models.ForeignKey(NTGNode, on_delete=models.CASCADE, related_name='cvtt_as_node_b')
    
    # Pivot clock (usually UTC reference)
    pivot_clock = models.ForeignKey(AtomicClock, on_delete=models.SET_NULL, null=True, related_name='cvtt_as_pivot')
    
    # Measurement data
    timestamp = models.DateTimeField()
    time_difference_ns = models.FloatField(help_text='Time difference between clocks in nanoseconds')
    uncertainty_ns = models.FloatField(help_text='Measurement uncertainty in nanoseconds')
    
    # GNSS constellation used
    gnss_constellation = models.CharField(max_length=20, default='GPS')
    satellites_used = ArrayField(models.CharField(max_length=10), default=list)
    
    # Quality indicators
    measurement_quality = models.FloatField(default=1.0, help_text='Quality score 0-1')
    is_valid = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'ntg_cvtt_measurements'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['node_a', 'node_b']),
        ]


class JammingEvent(models.Model):
    """GNSS jamming detection event"""
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    node = models.ForeignKey(NTGNode, on_delete=models.CASCADE, related_name='jamming_events')
    
    detected_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    affected_frequencies = ArrayField(models.CharField(max_length=20), default=list)
    signal_strength_reduction_db = models.FloatField()
    
    # Spectrum analysis data
    spectrum_data = models.JSONField(default=dict)
    estimated_direction_deg = models.FloatField(null=True, blank=True)
    
    # Impact assessment
    satellites_lost = models.IntegerField(default=0)
    timing_impact_ns = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'ntg_jamming_events'
        ordering = ['-detected_at']


class SpoofingEvent(models.Model):
    """GNSS spoofing detection event - multiple detection algorithms"""
    DETECTION_METHODS = [
        ('position_jump', 'Position Jump Detection'),
        ('clock_drift', 'Clock Drift Anomaly'),
        ('signal_power', 'Signal Power Anomaly'),
        ('doppler_shift', 'Doppler Shift Anomaly'),
        ('multi_receiver', 'Multi-Receiver Cross-Check'),
        ('crypto_auth', 'Cryptographic Authentication Failure'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    node = models.ForeignKey(NTGNode, on_delete=models.CASCADE, related_name='spoofing_events')
    
    detected_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    detection_method = models.CharField(max_length=30, choices=DETECTION_METHODS)
    confidence_score = models.FloatField(help_text='Detection confidence 0-1')
    
    # Spoofing characteristics
    fake_position_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    fake_position_lon = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    fake_time_offset_ns = models.FloatField(null=True, blank=True)
    
    # Evidence data
    evidence_data = models.JSONField(default=dict)
    affected_satellites = ArrayField(models.CharField(max_length=10), default=list)
    
    class Meta:
        db_table = 'ntg_spoofing_events'
        ordering = ['-detected_at']


class ClockStabilityTracking(models.Model):
    """Real-time clock stability tracking with early warning alerts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    atomic_clock = models.ForeignKey(AtomicClock, on_delete=models.CASCADE, related_name='stability_records')
    
    timestamp = models.DateTimeField()
    
    # Allan deviation measurements at different tau
    adev_1s = models.FloatField(help_text='Allan deviation at 1 second')
    adev_10s = models.FloatField(help_text='Allan deviation at 10 seconds')
    adev_100s = models.FloatField(help_text='Allan deviation at 100 seconds')
    adev_1000s = models.FloatField(help_text='Allan deviation at 1000 seconds')
    
    # UTC offset tracking
    utc_offset_ns = models.FloatField(help_text='Offset from UTC in nanoseconds')
    utc_drift_rate_ns_per_day = models.FloatField(help_text='Drift rate in ns/day')
    
    # Health indicators
    is_within_spec = models.BooleanField(default=True)
    degradation_detected = models.BooleanField(default=False)
    alert_generated = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'ntg_clock_stability'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['atomic_clock', 'timestamp']),
        ]


class AntennaEnvironment(models.Model):
    """GNSS antenna environment monitoring - signal quality, obstructions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    node = models.ForeignKey(NTGNode, on_delete=models.CASCADE, related_name='antenna_environment')
    
    timestamp = models.DateTimeField()
    
    # Signal strength by constellation
    gps_avg_cn0 = models.FloatField(help_text='Average GPS C/N0 in dB-Hz')
    galileo_avg_cn0 = models.FloatField(null=True, blank=True)
    glonass_avg_cn0 = models.FloatField(null=True, blank=True)
    beidou_avg_cn0 = models.FloatField(null=True, blank=True)
    
    # Satellite visibility
    total_satellites_visible = models.IntegerField()
    satellites_used_in_fix = models.IntegerField()
    
    # Obstruction analysis
    sky_view_percentage = models.FloatField(help_text='Percentage of sky visible')
    multipath_indicator = models.FloatField(help_text='Multipath error indicator')
    
    # Position solution quality
    hdop = models.FloatField()
    vdop = models.FloatField()
    pdop = models.FloatField()
    
    # Environment flags
    obstruction_detected = models.BooleanField(default=False)
    multipath_warning = models.BooleanField(default=False)
    interference_detected = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'ntg_antenna_environment'
        ordering = ['-timestamp']


class PTPLinkEvaluation(models.Model):
    """PTP GM/Client link stability evaluation using CVTT"""
    LINK_STATUS = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('degraded', 'Degraded'),
        ('poor', 'Poor'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    
    # PTP endpoints
    grandmaster_node = models.ForeignKey(NTGNode, on_delete=models.CASCADE, related_name='ptp_links_as_gm')
    client_node = models.ForeignKey(NTGNode, on_delete=models.CASCADE, related_name='ptp_links_as_client')
    
    timestamp = models.DateTimeField()
    
    # Link performance metrics
    path_delay_ns = models.FloatField(help_text='Mean path delay in nanoseconds')
    path_delay_variation_ns = models.FloatField(help_text='Path delay variation (PDV)')
    offset_from_master_ns = models.FloatField(help_text='Offset from master')
    
    # CVTT verification
    cvtt_verified = models.BooleanField(default=False)
    cvtt_discrepancy_ns = models.FloatField(null=True, blank=True, help_text='Discrepancy between PTP and CVTT')
    
    # Link quality assessment
    link_status = models.CharField(max_length=20, choices=LINK_STATUS)
    packet_loss_rate = models.FloatField(default=0)
    jitter_ns = models.FloatField()
    
    # Compliance check
    meets_itu_g8275_1 = models.BooleanField(default=False)
    meets_itu_g8275_2 = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'ntg_ptp_link_evaluation'
        ordering = ['-timestamp']


class TimingGridStatus(models.Model):
    """Overall National Timing Grid status dashboard data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Grid health summary
    total_nodes = models.IntegerField()
    nodes_online = models.IntegerField()
    nodes_degraded = models.IntegerField()
    nodes_offline = models.IntegerField()
    
    total_atomic_clocks = models.IntegerField()
    clocks_operational = models.IntegerField()
    clocks_in_holdover = models.IntegerField()
    
    # Active threats
    active_jamming_events = models.IntegerField(default=0)
    active_spoofing_events = models.IntegerField(default=0)
    
    # UTC traceability status
    utc_traceable = models.BooleanField(default=True)
    max_utc_offset_ns = models.FloatField()
    avg_utc_offset_ns = models.FloatField()
    
    # Grid resilience score (0-100)
    resilience_score = models.FloatField()
    
    class Meta:
        db_table = 'ntg_grid_status'
        ordering = ['-timestamp']
