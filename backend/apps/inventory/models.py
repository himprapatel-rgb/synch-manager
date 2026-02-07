"""
Synch-Manager Inventory Models

Defines Network Element (NE), Card, Port, and related inventory
entities for synchronization network management.
"""

from django.db import models
from django.utils import timezone


class NEType(models.TextChoices):
    TIMEPROVIDER_5000 = 'TP5000', 'TimeProvider 5000'
    TIMEPROVIDER_4100 = 'TP4100', 'TimeProvider 4100'
    TIMEPROVIDER_2700 = 'TP2700', 'TimeProvider 2700'
    TIMEPROVIDER_1100 = 'TP1100', 'TimeProvider 1100'
    TIMEHUB_5500 = 'TH5500', 'TimeHub 5500'
    TIMESOURCE_3600 = 'TS3600', 'TimeSource 3600'
    SSU_2000 = 'SSU2000', 'SSU 2000'
    SYNCSERVER_S650 = 'SS650', 'SyncServer S650'
    WHITE_RABBIT_SWITCH = 'WRS', 'White Rabbit Switch'
    PRS_4400 = 'PRS4400', 'TimeCesium PRS-4400'
    GENERIC_PTP_GM = 'PTP_GM', 'Generic PTP Grandmaster'
    GENERIC_PTP_BC = 'PTP_BC', 'Generic PTP Boundary Clock'
    ELORAN_RECEIVER = 'ELORAN', 'eLoran Receiver'
    LEO_PNT_RECEIVER = 'LEO_PNT', 'LEO PNT Receiver'
    CSAC_CLOCK = 'CSAC', 'Chip-Scale Atomic Clock'


class ManagementState(models.TextChoices):
    MANAGED = 'MANAGED', 'Managed'
    UNMANAGED = 'UNMANAGED', 'Unmanaged'
    UNAVAILABLE = 'UNAVAILABLE', 'Unavailable'
    MAINTENANCE = 'MAINTENANCE', 'Maintenance'


class AlarmSeverity(models.TextChoices):
    CRITICAL = 'CRITICAL', 'Critical'
    MAJOR = 'MAJOR', 'Major'
    MINOR = 'MINOR', 'Minor'
    WARNING = 'WARNING', 'Warning'
    CLEAR = 'CLEAR', 'Clear'


class NetworkElementGroup(models.Model):
    """Logical grouping of NEs for policy and alarm management."""
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, default='')
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_ne_group'
        ordering = ['name']

    def __str__(self):
        return self.name


class NetworkElement(models.Model):
    """Core model for a managed synchronization network element."""
    name = models.CharField(max_length=128, unique=True)
    ne_type = models.CharField(
        max_length=20, choices=NEType.choices,
        default=NEType.TIMEPROVIDER_5000
    )
    ip_address = models.GenericIPAddressField()
    snmp_community = models.CharField(max_length=64, default='public')
    snmp_version = models.CharField(
        max_length=4, choices=[('v1', 'v1'), ('v2c', 'v2c'), ('v3', 'v3')],
        default='v2c'
    )
    management_state = models.CharField(
        max_length=16, choices=ManagementState.choices,
        default=ManagementState.MANAGED
    )
    worst_alarm = models.CharField(
        max_length=10, choices=AlarmSeverity.choices,
        default=AlarmSeverity.CLEAR
    )
    group = models.ForeignKey(
        NetworkElementGroup, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='network_elements'
    )
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=256, blank=True, default='')
    sys_descr = models.CharField(max_length=512, blank=True, default='')
    sys_object_id = models.CharField(max_length=128, blank=True, default='')
    firmware_version = models.CharField(max_length=64, blank=True, default='')
    serial_number = models.CharField(max_length=64, blank=True, default='')
    hardware_revision = models.CharField(max_length=64, blank=True, default='')
    last_discovered = models.DateTimeField(null=True, blank=True)
    last_polled = models.DateTimeField(null=True, blank=True)
    uptime_seconds = models.BigIntegerField(default=0)
    notes = models.TextField(blank=True, default='')
    # Trust Score for Zero Trust Timing (0-100)
    trust_score = models.IntegerField(default=100)
    # Oscillator type for holdover prediction
    oscillator_type = models.CharField(
        max_length=16,
        choices=[
            ('OCXO', 'OCXO'), ('TCXO', 'TCXO'),
            ('Rb', 'Rubidium'), ('Cs', 'Cesium'),
            ('CSAC', 'Chip-Scale Atomic'),
        ],
        blank=True, default=''
    )
    # War Mode fields
    gnss_available = models.BooleanField(default=True)
    holdover_start = models.DateTimeField(null=True, blank=True)
    holdover_estimate_hours = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_network_element'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_ne_type_display()})'


class Card(models.Model):
    """Physical or logical card/module within an NE chassis."""
    network_element = models.ForeignKey(
        NetworkElement, on_delete=models.CASCADE, related_name='cards'
    )
    slot = models.CharField(max_length=16)
    card_type = models.CharField(max_length=64)
    part_number = models.CharField(max_length=64, blank=True, default='')
    serial_number = models.CharField(max_length=64, blank=True, default='')
    firmware_version = models.CharField(max_length=64, blank=True, default='')
    operational_state = models.CharField(
        max_length=16,
        choices=[
            ('IS', 'In Service'), ('OOS', 'Out of Service'),
            ('STDBY', 'Standby'), ('UNKNOWN', 'Unknown')
        ],
        default='UNKNOWN'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_card'
        unique_together = ['network_element', 'slot']
        ordering = ['network_element', 'slot']

    def __str__(self):
        return f'{self.network_element.name} Slot {self.slot}'


class Port(models.Model):
    """Physical port on a card or NE for timing signals."""
    card = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name='ports'
    )
    port_number = models.IntegerField()
    port_type = models.CharField(
        max_length=32,
        choices=[
            ('PTP', 'PTP'), ('NTP', 'NTP'), ('SyncE', 'SyncE'),
            ('1PPS', '1PPS'), ('10MHz', '10MHz'), ('ToD', 'ToD'),
            ('E1', 'E1'), ('T1', 'T1'), ('STM1', 'STM-1'),
            ('WR', 'White Rabbit'), ('OPTICAL', 'Optical Fiber'),
            ('RS232', 'RS-232 Serial'), ('ELORAN', 'eLoran'),
            ('LEO', 'LEO PNT'),
        ]
    )
    direction = models.CharField(
        max_length=8,
        choices=[('INPUT', 'Input'), ('OUTPUT', 'Output'), ('BIDIR', 'Bidirectional')],
        default='INPUT'
    )
    admin_state = models.CharField(
        max_length=16,
        choices=[('ENABLED', 'Enabled'), ('DISABLED', 'Disabled')],
        default='ENABLED'
    )
    operational_state = models.CharField(
        max_length=16,
        choices=[
            ('UP', 'Up'), ('DOWN', 'Down'),
            ('DEGRADED', 'Degraded'), ('UNKNOWN', 'Unknown')
        ],
        default='UNKNOWN'
    )
    signal_quality = models.CharField(
        max_length=8, blank=True, default='',
        help_text='SSM/QL value e.g. PRS, SSU_A, SSU_B, SEC, DNU'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_port'
        unique_together = ['card', 'port_number']
        ordering = ['card', 'port_number']

    def __str__(self):
        return f'{self.card} Port {self.port_number} ({self.port_type})'


class TimingLink(models.Model):
    """Represents a timing distribution link between two NE ports."""
    LINK_TYPES = [
        ('PTP', 'PTP'), ('SyncE', 'SyncE'), ('WR', 'White Rabbit'),
        ('1PPS', '1PPS Cable'), ('FIBER_OPTICAL', 'Optical Fiber Timing'),
        ('NTP', 'NTP'),
    ]
    source_port = models.ForeignKey(
        Port, on_delete=models.CASCADE, related_name='outgoing_links'
    )
    destination_port = models.ForeignKey(
        Port, on_delete=models.CASCADE, related_name='incoming_links'
    )
    link_type = models.CharField(max_length=20, choices=LINK_TYPES)
    estimated_delay_ns = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_timing_link'

    def __str__(self):
        return f'{self.source_port} -> {self.destination_port} ({self.link_type})'
