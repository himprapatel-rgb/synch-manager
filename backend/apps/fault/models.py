"""
Synch-Manager Fault Management Models

Alarm and Event models following ITU-T X.733/X.734 alarm standards
for synchronization network fault management.
"""

from django.db import models
from django.conf import settings


class AlarmState(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    ACKNOWLEDGED = 'ACKNOWLEDGED', 'Acknowledged'
    CLEARED = 'CLEARED', 'Cleared'


class AlarmSeverity(models.TextChoices):
    CRITICAL = 'CRITICAL', 'Critical'
    MAJOR = 'MAJOR', 'Major'
    MINOR = 'MINOR', 'Minor'
    WARNING = 'WARNING', 'Warning'
    CLEAR = 'CLEAR', 'Clear'


class AlarmCategory(models.TextChoices):
    COMMUNICATIONS = 'COMMS', 'Communications'
    QUALITY_OF_SERVICE = 'QOS', 'Quality of Service'
    PROCESSING = 'PROC', 'Processing Error'
    EQUIPMENT = 'EQUIP', 'Equipment'
    ENVIRONMENTAL = 'ENV', 'Environmental'
    TIMING = 'TIMING', 'Timing/Sync'
    GNSS = 'GNSS', 'GNSS/Satellite'
    SECURITY = 'SEC', 'Security'
    WAR_MODE = 'WAR', 'War Mode'


class Alarm(models.Model):
    """Active or historical alarm raised by an NE."""
    network_element = models.ForeignKey(
        'inventory.NetworkElement',
        on_delete=models.CASCADE, related_name='alarms'
    )
    alarm_type = models.CharField(max_length=64)
    severity = models.CharField(
        max_length=10, choices=AlarmSeverity.choices
    )
    state = models.CharField(
        max_length=16, choices=AlarmState.choices,
        default=AlarmState.ACTIVE
    )
    category = models.CharField(
        max_length=8, choices=AlarmCategory.choices,
        default=AlarmCategory.TIMING
    )
    probable_cause = models.CharField(max_length=128, blank=True, default='')
    description = models.TextField(blank=True, default='')
    additional_info = models.JSONField(default=dict, blank=True)
    # Source identification
    managed_object = models.CharField(
        max_length=256, blank=True, default='',
        help_text='Card/port/subsystem that raised the alarm'
    )
    # SNMP trap details
    trap_oid = models.CharField(max_length=256, blank=True, default='')
    trap_varbinds = models.JSONField(default=dict, blank=True)
    # Lifecycle timestamps
    raised_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    cleared_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='acknowledged_alarms'
    )
    ack_comment = models.TextField(blank=True, default='')
    # GNSS-specific fields
    is_gnss_related = models.BooleanField(default=False)
    trust_impact = models.IntegerField(
        default=0,
        help_text='Trust score reduction caused by this alarm'
    )

    class Meta:
        db_table = 'fault_alarm'
        ordering = ['-raised_at']
        indexes = [
            models.Index(fields=['state', 'severity']),
            models.Index(fields=['network_element', 'state']),
            models.Index(fields=['raised_at']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return (
            f'{self.network_element.name}: '
            f'{self.alarm_type} ({self.severity})'
        )


class Event(models.Model):
    """Informational event log entry from an NE or the system."""
    EVENT_SOURCES = [
        ('SNMP_TRAP', 'SNMP Trap'),
        ('POLLING', 'Polling'),
        ('SYSTEM', 'System'),
        ('USER', 'User Action'),
        ('WAR_MODE', 'War Mode Engine'),
        ('TRUST_ENGINE', 'Zero Trust Engine'),
        ('GNSS_PEER', 'GNSS Peer Resilience'),
    ]
    network_element = models.ForeignKey(
        'inventory.NetworkElement',
        on_delete=models.CASCADE, related_name='events',
        null=True, blank=True
    )
    source = models.CharField(max_length=16, choices=EVENT_SOURCES)
    event_type = models.CharField(max_length=64)
    severity = models.CharField(
        max_length=10, choices=AlarmSeverity.choices,
        default=AlarmSeverity.CLEAR
    )
    description = models.TextField(blank=True, default='')
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fault_event'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['source', 'event_type']),
        ]

    def __str__(self):
        ne_name = self.network_element.name if self.network_element else 'SYSTEM'
        return f'{ne_name}: {self.event_type} at {self.timestamp}'


class AlarmPolicy(models.Model):
    """Rules for alarm suppression, escalation, or forwarding."""
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    # Match criteria
    match_ne_type = models.CharField(max_length=20, blank=True, default='')
    match_alarm_type = models.CharField(max_length=64, blank=True, default='')
    match_severity = models.CharField(
        max_length=10, choices=AlarmSeverity.choices,
        blank=True, default=''
    )
    match_category = models.CharField(
        max_length=8, choices=AlarmCategory.choices,
        blank=True, default=''
    )
    # Actions
    ACTION_CHOICES = [
        ('SUPPRESS', 'Suppress Alarm'),
        ('ESCALATE', 'Escalate Severity'),
        ('FORWARD_SNMP', 'Forward via SNMP NBI'),
        ('FORWARD_SYSLOG', 'Forward via Syslog'),
        ('FORWARD_KAFKA', 'Forward via Kafka'),
        ('AUTO_ACK', 'Auto-Acknowledge'),
    ]
    action = models.CharField(max_length=16, choices=ACTION_CHOICES)
    action_params = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fault_alarm_policy'
        verbose_name_plural = 'Alarm policies'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.action})'
