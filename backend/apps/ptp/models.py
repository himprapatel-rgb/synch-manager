"""
PTP Client Management Models for Synch-Manager.

IEEE 1588 PTP client discovery, monitoring, LinuxPTP integration,
and synchronization topology management.
"""

from django.db import models
from django.utils import timezone


class PTPDomain(models.Model):
    """PTP domain grouping."""

    domain_number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    profile = models.CharField(
        max_length=50,
        choices=[
            ('DEFAULT', 'Default (IEEE 1588)'),
            ('G8275_1', 'ITU-T G.8275.1 (Full Timing)'),
            ('G8275_2', 'ITU-T G.8275.2 (Partial Timing)'),
            ('POWER', 'IEEE C37.238 (Power)'),
            ('SMPTE', 'SMPTE ST 2059 (Media)'),
        ],
        default='DEFAULT',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Domain {self.domain_number} ({self.name or self.profile})'


class PTPGrandmaster(models.Model):
    """PTP Grandmaster clock."""

    class ClockClass(models.IntegerChoices):
        PRIMARY_REF = 6, 'Primary Reference (6)'
        PRIMARY_REF_HOLDOVER = 7, 'Primary Ref Holdover (7)'
        APPLICATION_SPECIFIC = 13, 'App-Specific (13)'
        APPLICATION_HOLDOVER = 14, 'App Holdover (14)'
        SLAVE_ONLY = 255, 'Slave Only (255)'

    network_element = models.ForeignKey(
        'inventory.NetworkElement', on_delete=models.CASCADE,
        related_name='ptp_grandmasters',
    )
    clock_identity = models.CharField(
        max_length=24,
        help_text='EUI-64 clock identity (e.g. 001122.fffe.334455)',
    )
    domain = models.ForeignKey(
        PTPDomain, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='grandmasters',
    )
    clock_class = models.PositiveIntegerField(
        choices=ClockClass.choices, default=ClockClass.PRIMARY_REF,
    )
    clock_accuracy = models.CharField(max_length=10, default='0x21')
    priority1 = models.PositiveIntegerField(default=128)
    priority2 = models.PositiveIntegerField(default=128)
    time_source = models.CharField(
        max_length=20,
        choices=[
            ('ATOMIC_CLOCK', 'Atomic Clock'),
            ('GNSS', 'GNSS'),
            ('PTP', 'PTP'),
            ('NTP', 'NTP'),
            ('HAND_SET', 'Hand Set'),
            ('OTHER', 'Other'),
            ('INTERNAL_OSCILLATOR', 'Internal Oscillator'),
        ],
        default='GNSS',
    )
    two_step = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['network_element', 'clock_identity']

    def __str__(self):
        return f'GM {self.clock_identity} on {self.network_element}'


class PTPClient(models.Model):
    """PTP slave/client clock being monitored."""

    class PortState(models.TextChoices):
        INITIALIZING = 'INITIALIZING', 'Initializing'
        FAULTY = 'FAULTY', 'Faulty'
        DISABLED = 'DISABLED', 'Disabled'
        LISTENING = 'LISTENING', 'Listening'
        PRE_MASTER = 'PRE_MASTER', 'Pre-Master'
        MASTER = 'MASTER', 'Master'
        PASSIVE = 'PASSIVE', 'Passive'
        UNCALIBRATED = 'UNCALIBRATED', 'Uncalibrated'
        SLAVE = 'SLAVE', 'Slave'

    hostname = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    clock_identity = models.CharField(max_length=24, blank=True)
    port_state = models.CharField(
        max_length=20, choices=PortState.choices,
        default=PortState.INITIALIZING,
    )
    grandmaster = models.ForeignKey(
        PTPGrandmaster, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='clients',
    )
    domain = models.ForeignKey(
        PTPDomain, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='clients',
    )
    ptp_implementation = models.CharField(
        max_length=50,
        choices=[
            ('LINUXPTP', 'LinuxPTP (ptp4l)'),
            ('PTP4L_CHRONY', 'LinuxPTP + Chrony'),
            ('WINDOWS_PTP', 'Windows PTP'),
            ('SFPTPD', 'Xilinx sfptpd'),
            ('VENDOR_SPECIFIC', 'Vendor Specific'),
            ('UNKNOWN', 'Unknown'),
        ],
        default='LINUXPTP',
    )
    transport = models.CharField(
        max_length=20,
        choices=[
            ('UDP_IPV4', 'UDP/IPv4'),
            ('UDP_IPV6', 'UDP/IPv6'),
            ('IEEE_802_3', 'IEEE 802.3 (L2)'),
        ],
        default='UDP_IPV4',
    )
    is_monitored = models.BooleanField(default=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['ip_address', 'clock_identity']

    def __str__(self):
        return f'PTP Client {self.hostname} ({self.ip_address})'


class PTPClientMetrics(models.Model):
    """Time-series metrics for PTP clients."""

    client = models.ForeignKey(
        PTPClient, on_delete=models.CASCADE, related_name='metrics',
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    offset_from_master_ns = models.FloatField(
        help_text='Offset from master in nanoseconds',
    )
    mean_path_delay_ns = models.FloatField(
        help_text='Mean path delay in nanoseconds',
    )
    frequency_offset_ppb = models.FloatField(
        default=0.0,
        help_text='Frequency offset in parts-per-billion',
    )
    port_state = models.CharField(max_length=20, blank=True)
    gm_clock_identity = models.CharField(max_length=24, blank=True)
    gm_clock_class = models.PositiveIntegerField(null=True, blank=True)
    steps_removed = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['client', '-timestamp']),
        ]

    def __str__(self):
        return (
            f'{self.client} @ {self.timestamp}: '
            f'offset={self.offset_from_master_ns}ns'
        )


class PTPTopologyLink(models.Model):
    """Represents a PTP timing link between two nodes."""

    class LinkType(models.TextChoices):
        PTP = 'PTP', 'PTP'
        WHITE_RABBIT = 'WHITE_RABBIT', 'White Rabbit'
        SYNCE = 'SYNCE', 'SyncE'
        NTP = 'NTP', 'NTP'
        OPTICAL_FIBER = 'OPTICAL_FIBER', 'Optical Fiber'

    source_ne = models.ForeignKey(
        'inventory.NetworkElement', on_delete=models.CASCADE,
        related_name='outgoing_links',
    )
    target_ne = models.ForeignKey(
        'inventory.NetworkElement', on_delete=models.CASCADE,
        related_name='incoming_links',
    )
    link_type = models.CharField(
        max_length=20, choices=LinkType.choices, default=LinkType.PTP,
    )
    asymmetry_ns = models.FloatField(
        default=0.0, help_text='Known path asymmetry in nanoseconds',
    )
    is_active = models.BooleanField(default=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    last_verified = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['source_ne', 'target_ne', 'link_type']

    def __str__(self):
        return (
            f'{self.source_ne} -> {self.target_ne} '
            f'({self.get_link_type_display()})'
        )


class LinuxPTPInstance(models.Model):
    """Tracks a ptp4l / phc2sys instance on a managed host."""

    class ServiceState(models.TextChoices):
        RUNNING = 'RUNNING', 'Running'
        STOPPED = 'STOPPED', 'Stopped'
        ERROR = 'ERROR', 'Error'
        UNKNOWN = 'UNKNOWN', 'Unknown'

    client = models.OneToOneField(
        PTPClient, on_delete=models.CASCADE,
        related_name='linuxptp_instance',
    )
    ptp4l_config = models.JSONField(
        default=dict, help_text='ptp4l configuration parameters',
    )
    phc2sys_config = models.JSONField(
        default=dict, help_text='phc2sys configuration parameters',
    )
    service_state = models.CharField(
        max_length=10, choices=ServiceState.choices,
        default=ServiceState.UNKNOWN,
    )
    ptp4l_version = models.CharField(max_length=30, blank=True)
    interface = models.CharField(
        max_length=50, blank=True, help_text='Network interface (e.g. eth0)',
    )
    hardware_timestamping = models.BooleanField(default=True)
    last_config_push = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'LinuxPTP on {self.client} ({self.service_state})'
