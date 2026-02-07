"""
Performance Management Models for Synch-Manager.

Stores time-series performance metrics for PTP/NTP/SyncE network elements:
- MTIE (Maximum Time Interval Error)
- TDEV (Time Deviation)
- Phase offset and frequency offset
- C/N0 (Carrier-to-Noise) for GNSS
- White Rabbit link delay measurements

All time-series data is stored in TimescaleDB hypertables for efficient
time-range queries and downsampling.
"""

import uuid
from django.db import models
from django.utils import timezone


class PerformanceMetric(models.Model):
    """Base time-series metric stored in TimescaleDB hypertable."""

    class MetricType(models.TextChoices):
        MTIE = 'MTIE', 'Maximum Time Interval Error'
        TDEV = 'TDEV', 'Time Deviation'
        PHASE_OFFSET = 'PHASE_OFFSET', 'Phase Offset (ns)'
        FREQ_OFFSET = 'FREQ_OFFSET', 'Frequency Offset (ppb)'
        PTP_DELAY = 'PTP_DELAY', 'PTP Path Delay (ns)'
        WR_LINK_DELAY = 'WR_LINK_DELAY', 'White Rabbit Link Delay (ps)'
        CNO = 'CNO', 'Carrier-to-Noise Ratio (dB-Hz)'
        SATELLITES = 'SATELLITES', 'Tracked Satellite Count'
        HOLDOVER_ERROR = 'HOLDOVER_ERROR', 'CSAC Holdover Error (ns)'
        SYNC_MESH_SCORE = 'SYNC_MESH_SCORE', 'Sync Mesh Score (0-100)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    network_element = models.ForeignKey(
        'inventory.NetworkElement',
        on_delete=models.CASCADE,
        related_name='performance_metrics',
        db_index=True,
    )
    metric_type = models.CharField(
        max_length=30,
        choices=MetricType.choices,
        db_index=True,
    )
    value = models.FloatField(help_text='Metric value')
    unit = models.CharField(max_length=20, blank=True, default='')
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    # Optional context fields
    interface_name = models.CharField(
        max_length=100, blank=True, default='',
        help_text='Port/interface the metric was collected from',
    )
    satellite_prn = models.CharField(
        max_length=10, blank=True, default='',
        help_text='GNSS satellite PRN (e.g., G01, E05, R12)',
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(
                fields=['network_element', 'metric_type', '-timestamp'],
                name='idx_perf_ne_type_ts',
            ),
        ]
        # TimescaleDB hypertable created via migration:
        # SELECT create_hypertable('performance_performancemetric', 'timestamp');

    def __str__(self):
        return (
            f"{self.network_element} | {self.get_metric_type_display()} "
            f"= {self.value} @ {self.timestamp:%Y-%m-%d %H:%M:%S}"
        )


class MTIEMask(models.Model):
    """ITU-T G.823/G.824 MTIE mask definition for compliance checking."""

    class Standard(models.TextChoices):
        G823_PDH = 'G823_PDH', 'ITU-T G.823 PDH'
        G824_DS1 = 'G824_DS1', 'ITU-T G.824 DS1'
        G8261 = 'G8261', 'ITU-T G.8261 SyncE'
        G8262 = 'G8262', 'ITU-T G.8262 EEC'
        G8272 = 'G8272', 'ITU-T G.8272 PRTC'
        G8275_1 = 'G8275_1', 'ITU-T G.8275.1 PTP Telecom'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    standard = models.CharField(
        max_length=20, choices=Standard.choices,
    )
    observation_interval_sec = models.FloatField(
        help_text='Observation interval tau (seconds)',
    )
    mtie_limit_ns = models.FloatField(
        help_text='MTIE limit at this observation interval (nanoseconds)',
    )

    class Meta:
        ordering = ['standard', 'observation_interval_sec']
        unique_together = ['standard', 'observation_interval_sec']

    def __str__(self):
        return f"{self.get_standard_display()} | tau={self.observation_interval_sec}s | limit={self.mtie_limit_ns}ns"


class SyncMeshScore(models.Model):
    """Network-wide synchronization health score computed periodically."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    overall_score = models.IntegerField(
        help_text='Network-wide sync mesh score 0-100',
    )

    # Component scores
    gnss_health_score = models.IntegerField(default=0)
    ptp_accuracy_score = models.IntegerField(default=0)
    wr_link_score = models.IntegerField(default=0)
    holdover_readiness_score = models.IntegerField(default=0)
    peer_connectivity_score = models.IntegerField(default=0)

    # Counts
    total_nodes = models.IntegerField(default=0)
    gnss_locked_nodes = models.IntegerField(default=0)
    ptp_synced_nodes = models.IntegerField(default=0)
    holdover_nodes = models.IntegerField(default=0)
    failed_nodes = models.IntegerField(default=0)

    # War mode status
    war_mode_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        status = 'WAR MODE' if self.war_mode_active else 'NORMAL'
        return f"SyncMesh {self.overall_score}/100 [{status}] @ {self.timestamp:%Y-%m-%d %H:%M}"


class PerformanceThreshold(models.Model):
    """Configurable thresholds that trigger alarms when breached."""

    class Severity(models.TextChoices):
        WARNING = 'WARNING', 'Warning'
        MINOR = 'MINOR', 'Minor'
        MAJOR = 'MAJOR', 'Major'
        CRITICAL = 'CRITICAL', 'Critical'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    metric_type = models.CharField(
        max_length=30,
        choices=PerformanceMetric.MetricType.choices,
    )
    upper_threshold = models.FloatField(
        null=True, blank=True,
        help_text='Alarm if value exceeds this',
    )
    lower_threshold = models.FloatField(
        null=True, blank=True,
        help_text='Alarm if value drops below this',
    )
    severity = models.CharField(
        max_length=10, choices=Severity.choices, default=Severity.WARNING,
    )
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['metric_type', 'severity']

    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"
