"""
War Mode Models for Synch-Manager.

Django ORM models for tactical timing operations including
war mode sessions, timing source failover tracking,
holdover events, and multi-domain coordination.
"""

import uuid
from django.db import models
from django.utils import timezone


class WarModeLevel(models.TextChoices):
    PEACETIME = 'PEACETIME', 'Peacetime - Normal operations'
    ELEVATED = 'ELEVATED', 'Elevated - Increased threat awareness'
    TACTICAL = 'TACTICAL', 'Tactical - Active threat environment'
    CRITICAL = 'CRITICAL', 'Critical - GNSS denied, contested'
    HOLDOVER = 'HOLDOVER', 'Holdover - All external sources lost'


class ThreatType(models.TextChoices):
    BENIGN = 'BENIGN', 'Benign'
    JAMMING = 'JAMMING', 'GNSS Jamming'
    SPOOFING = 'SPOOFING', 'GNSS Spoofing'
    KINETIC = 'KINETIC', 'Kinetic Attack'
    CYBER = 'CYBER', 'Cyber Attack'
    EMP = 'EMP', 'Electromagnetic Pulse'
    MULTI_DOMAIN = 'MULTI_DOMAIN', 'Multi-Domain Combined'


class WarModeSession(models.Model):
    """Tracks a war mode activation session with full lifecycle."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level = models.CharField(
        max_length=12, choices=WarModeLevel.choices,
        default=WarModeLevel.PEACETIME,
    )
    threat_type = models.CharField(
        max_length=15, choices=ThreatType.choices,
        default=ThreatType.BENIGN,
    )
    activated_at = models.DateTimeField(default=timezone.now, db_index=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    activated_by = models.CharField(
        max_length=150, default='system',
        help_text='User or system that triggered war mode',
    )
    reason = models.TextField(blank=True, default='')
    threat_indicators = models.JSONField(
        default=dict, blank=True,
        help_text='Threat indicator data that triggered this session',
    )

    class Meta:
        ordering = ['-activated_at']
        verbose_name = 'War Mode Session'

    def __str__(self):
        status = 'ACTIVE' if self.is_active else 'ENDED'
        return f'{self.get_level_display()} [{status}] @ {self.activated_at}'


class WarModeTransition(models.Model):
    """Records each war mode level transition."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        WarModeSession, on_delete=models.CASCADE,
        related_name='transitions',
    )
    from_level = models.CharField(max_length=12, choices=WarModeLevel.choices)
    to_level = models.CharField(max_length=12, choices=WarModeLevel.choices)
    threat_indicators = models.JSONField(default=dict, blank=True)
    transitioned_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-transitioned_at']

    def __str__(self):
        return f'{self.from_level} -> {self.to_level} @ {self.transitioned_at}'


class TimingSourceFailover(models.Model):
    """Logs each timing source switchover during war mode."""

    class SourceType(models.TextChoices):
        GNSS_PRIMARY = 'GNSS_PRI', 'GNSS Primary'
        GNSS_SECONDARY = 'GNSS_SEC', 'GNSS Secondary'
        LEO_PNT = 'LEO_PNT', 'LEO-PNT Satellite'
        ELORAN = 'ELORAN', 'eLoran'
        WHITE_RABBIT = 'WR', 'White Rabbit'
        CSAC = 'CSAC', 'Chip-Scale Atomic Clock'
        OCXO = 'OCXO', 'Oven-Controlled Crystal Oscillator'
        RUBIDIUM = 'RUBIDIUM', 'Rubidium Oscillator'
        CESIUM = 'CESIUM', 'Cesium PRS-4400'
        HOLDOVER = 'HOLDOVER', 'Holdover (free-running)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    network_element = models.ForeignKey(
        'inventory.NetworkElement',
        on_delete=models.CASCADE,
        related_name='timing_failovers',
    )
    session = models.ForeignKey(
        WarModeSession, on_delete=models.CASCADE,
        related_name='failovers', null=True, blank=True,
    )
    from_source = models.CharField(
        max_length=10, choices=SourceType.choices,
    )
    to_source = models.CharField(
        max_length=10, choices=SourceType.choices,
    )
    reason = models.TextField(
        blank=True, default='',
        help_text='Why the failover occurred',
    )
    switched_at = models.DateTimeField(default=timezone.now, db_index=True)
    switchover_duration_ms = models.FloatField(
        null=True, blank=True,
        help_text='Time to complete switchover in milliseconds',
    )

    class Meta:
        ordering = ['-switched_at']

    def __str__(self):
        return (
            f'{self.network_element}: '
            f'{self.from_source} -> {self.to_source} @ {self.switched_at}'
        )


class HoldoverEvent(models.Model):
    """Tracks holdover periods when no external timing is available."""

    class QualityLevel(models.TextChoices):
        EXCELLENT = 'EXCELLENT', 'Excellent (< 1us/day)'
        GOOD = 'GOOD', 'Good (< 10us/day)'
        ACCEPTABLE = 'ACCEPTABLE', 'Acceptable (< 100us/day)'
        DEGRADED = 'DEGRADED', 'Degraded (< 1ms/day)'
        POOR = 'POOR', 'Poor (> 1ms/day)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    network_element = models.ForeignKey(
        'inventory.NetworkElement',
        on_delete=models.CASCADE,
        related_name='holdover_events',
    )
    session = models.ForeignKey(
        WarModeSession, on_delete=models.SET_NULL,
        related_name='holdover_events', null=True, blank=True,
    )
    oscillator_type = models.CharField(
        max_length=10,
        choices=TimingSourceFailover.SourceType.choices,
        default=TimingSourceFailover.SourceType.CSAC,
    )
    quality = models.CharField(
        max_length=12, choices=QualityLevel.choices,
        default=QualityLevel.EXCELLENT,
    )
    drift_rate_ppb = models.FloatField(
        default=0.0,
        help_text='Measured drift rate in parts-per-billion',
    )
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_drift_ns = models.FloatField(
        default=0.0,
        help_text='Accumulated time drift in nanoseconds',
    )

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        status = 'ACTIVE' if self.is_active else 'ENDED'
        return (
            f'{self.network_element}: Holdover [{status}] '
            f'{self.get_quality_display()} @ {self.started_at}'
        )


class TacticalDomain(models.Model):
    """Operational domain for multi-domain timing coordination."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, default='')
    network_elements = models.ManyToManyField(
        'inventory.NetworkElement',
        related_name='tactical_domains',
        blank=True,
    )
    sync_mesh_enabled = models.BooleanField(
        default=False,
        help_text='Peer-to-peer timing mesh active for this domain',
    )
    emcon_active = models.BooleanField(
        default=False,
        help_text='Emissions Control mode (radio silence)',
    )
    current_level = models.CharField(
        max_length=12, choices=WarModeLevel.choices,
        default=WarModeLevel.PEACETIME,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} [{self.get_current_level_display()}]'


class CSACStatus(models.Model):
    """Real-time CSAC (Chip-Scale Atomic Clock) status per NE."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    network_element = models.OneToOneField(
        'inventory.NetworkElement',
        on_delete=models.CASCADE,
        related_name='csac_status',
    )
    is_active = models.BooleanField(default=False)
    is_ready = models.BooleanField(
        default=False,
        help_text='True when warmup complete and CSAC is locked',
    )
    temperature_c = models.FloatField(default=25.0)
    power_watts = models.FloatField(default=0.0)
    allan_deviation = models.FloatField(
        default=2e-10,
        help_text='Allan deviation at 1 second',
    )
    drift_rate_per_day = models.FloatField(
        default=5e-11,
        help_text='Drift rate in seconds per day',
    )
    activated_at = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'CSAC Status'
        verbose_name_plural = 'CSAC Statuses'

    def __str__(self):
        state = 'ACTIVE' if self.is_active else 'INACTIVE'
        return f'{self.network_element}: CSAC [{state}]'
