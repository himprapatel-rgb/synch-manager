"""
Security & GNSS Resilience Models for Synch-Manager.

Manages Zero Trust timing, GNSS threat detection, War Mode state,
audit logging, and peer trust relationships.
"""

import uuid
from django.db import models
from django.utils import timezone


class GNSSStatus(models.Model):
    """Real-time GNSS receiver status per network element."""

    class TimingSource(models.TextChoices):
        GNSS = 'GNSS', 'GNSS Primary'
        WHITE_RABBIT = 'WR', 'White Rabbit PTP'
        CSAC = 'CSAC', 'Chip-Scale Atomic Clock'
        ELORAN = 'ELORAN', 'eLoran'
        LEO_PNT = 'LEO_PNT', 'LEO-PNT Satellite'
        PEER = 'PEER', 'Peer Backup'
        FREERUN = 'FREERUN', 'Free-Running'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    network_element = models.OneToOneField(
        'inventory.NetworkElement',
        on_delete=models.CASCADE,
        related_name='gnss_status',
    )
    gnss_locked = models.BooleanField(default=False)
    satellites_tracked = models.IntegerField(default=0)
    c_no_avg_dbhz = models.FloatField(default=0.0, help_text='Average C/N0 in dB-Hz')
    position_lat = models.FloatField(null=True, blank=True)
    position_lon = models.FloatField(null=True, blank=True)
    time_source = models.CharField(
        max_length=10, choices=TimingSource.choices, default=TimingSource.GNSS,
    )
    trust_score = models.IntegerField(
        default=0, help_text='Zero Trust score 0-100',
    )
    spoofing_detected = models.BooleanField(default=False)
    jamming_detected = models.BooleanField(default=False)
    osnma_authenticated = models.BooleanField(default=False)
    holdover_elapsed_sec = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'GNSS Statuses'

    def __str__(self):
        return f"{self.network_element} | {self.get_time_source_display()} | Trust: {self.trust_score}"


class ThreatEvent(models.Model):
    """Logged GNSS/timing threat events (spoofing, jamming, anomalies)."""

    class ThreatType(models.TextChoices):
        SPOOFING = 'SPOOFING', 'GNSS Spoofing Detected'
        JAMMING = 'JAMMING', 'GNSS Jamming Detected'
        POSITION_JUMP = 'POS_JUMP', 'Anomalous Position Jump'
        TIME_JUMP = 'TIME_JUMP', 'Anomalous Time Jump'
        OSNMA_FAILURE = 'OSNMA_FAIL', 'OSNMA Authentication Failed'
        CNO_DROP = 'CNO_DROP', 'Sudden C/N0 Drop'
        TRUST_DROP = 'TRUST_DROP', 'Trust Score Below Threshold'

    class Severity(models.TextChoices):
        INFO = 'INFO', 'Informational'
        WARNING = 'WARNING', 'Warning'
        CRITICAL = 'CRITICAL', 'Critical'
        URGENT = 'URGENT', 'Urgent'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    network_element = models.ForeignKey(
        'inventory.NetworkElement',
        on_delete=models.CASCADE,
        related_name='threat_events',
    )
    threat_type = models.CharField(max_length=15, choices=ThreatType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices)
    description = models.TextField()
    detected_at = models.DateTimeField(default=timezone.now, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved = models.BooleanField(default=False)

    # Evidence data
    evidence = models.JSONField(
        default=dict, blank=True,
        help_text='Raw detection data (C/N0 values, position delta, etc.)',
    )

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.get_threat_type_display()} [{self.get_severity_display()}] @ {self.detected_at}"


class WarModeState(models.Model):
    """Network-wide War Mode state singleton."""

    class State(models.TextChoices):
        NORMAL = 'NORMAL', 'Normal Operations'
        DEGRADED = 'DEGRADED', 'Degraded - Elevated Monitoring'
        WAR_MODE = 'WAR_MODE', 'War Mode - Backup Timing Active'
        RECOVERY = 'RECOVERY', 'Recovery - Re-acquiring GNSS'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    current_state = models.CharField(
        max_length=10, choices=State.choices, default=State.NORMAL,
    )
    activated_at = models.DateTimeField(null=True, blank=True)
    activated_by = models.CharField(max_length=100, blank=True, default='')
    reason = models.TextField(blank=True, default='')
    gnss_denied_count = models.IntegerField(default=0)
    total_node_count = models.IntegerField(default=0)
    last_state_change = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'War Mode State'

    def save(self, *args, **kwargs):
        # Singleton pattern: only one instance allowed
        self.pk = self.pk or uuid.uuid4()
        super().save(*args, **kwargs)
        WarModeState.objects.exclude(pk=self.pk).delete()

    def __str__(self):
        return f"War Mode: {self.get_current_state_display()}"


class AuditLogEntry(models.Model):
    """Tamper-evident audit log for timing security events."""

    class EventType(models.TextChoices):
        SOURCE_CHANGE = 'SOURCE_CHANGE', 'Timing Source Changed'
        SPOOFING_DETECTED = 'SPOOFING_DETECTED', 'Spoofing Attack Identified'
        JAMMING_DETECTED = 'JAMMING_DETECTED', 'Jamming Detected'
        WAR_MODE_ACTIVATED = 'WAR_MODE_ON', 'War Mode Activated'
        WAR_MODE_DEACTIVATED = 'WAR_MODE_OFF', 'War Mode Deactivated'
        HOLDOVER_STARTED = 'HOLDOVER_ON', 'CSAC Holdover Started'
        HOLDOVER_ENDED = 'HOLDOVER_OFF', 'CSAC Holdover Ended'
        PEER_FAILOVER = 'PEER_FAILOVER', 'Peer Backup Activated'
        TRUST_SCORE_CHANGE = 'TRUST_CHANGE', 'Trust Score Changed'
        CONFIG_CHANGE = 'CONFIG_CHANGE', 'Security Config Modified'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    network_element = models.ForeignKey(
        'inventory.NetworkElement',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs',
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    actor = models.CharField(
        max_length=100, blank=True, default='system',
        help_text='User or system that triggered the event',
    )
    details = models.JSONField(default=dict, blank=True)
    previous_hash = models.CharField(
        max_length=64, blank=True, default='',
        help_text='SHA-256 of previous log entry for tamper detection',
    )
    entry_hash = models.CharField(
        max_length=64, blank=True, default='',
        help_text='SHA-256 hash of this entry',
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.get_event_type_display()}"
