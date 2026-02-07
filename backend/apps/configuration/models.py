"""
Configuration Management Models for Synch-Manager.

Policy-based configuration management with compliance auditing,
GitOps-style version control, and Zero Trust timing validation.
"""

from django.db import models
from django.utils import timezone


class ConfigurationPolicy(models.Model):
    """Reusable configuration policy template."""

    class PolicyType(models.TextChoices):
        PTP_PROFILE = 'PTP_PROFILE', 'PTP Profile'
        NTP_CONFIG = 'NTP_CONFIG', 'NTP Configuration'
        SYNCE_CONFIG = 'SYNCE_CONFIG', 'SyncE Configuration'
        GNSS_CONFIG = 'GNSS_CONFIG', 'GNSS Configuration'
        SECURITY_CONFIG = 'SECURITY_CONFIG', 'Security Configuration'
        FIRMWARE_POLICY = 'FIRMWARE_POLICY', 'Firmware Policy'
        TIMING_SOURCE = 'TIMING_SOURCE', 'Timing Source Priority'
        WAR_MODE_POLICY = 'WAR_MODE_POLICY', 'War Mode Policy'

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    policy_type = models.CharField(
        max_length=30, choices=PolicyType.choices
    )
    config_data = models.JSONField(
        help_text='Policy configuration as structured JSON'
    )
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Configuration policies'

    def __str__(self):
        return f'{self.name} v{self.version} ({self.get_policy_type_display()})'


class PolicyGroup(models.Model):
    """Group of policies applied to one or more NEs."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    policies = models.ManyToManyField(
        ConfigurationPolicy, related_name='groups', blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PolicyAssignment(models.Model):
    """Tracks which policy group is assigned to which NE."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPLIED = 'APPLIED', 'Applied'
        FAILED = 'FAILED', 'Failed'
        ROLLED_BACK = 'ROLLED_BACK', 'Rolled Back'

    policy_group = models.ForeignKey(
        PolicyGroup, on_delete=models.CASCADE, related_name='assignments'
    )
    network_element = models.ForeignKey(
        'inventory.NetworkElement', on_delete=models.CASCADE,
        related_name='policy_assignments'
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    applied_at = models.DateTimeField(null=True, blank=True)
    applied_by = models.CharField(max_length=150, blank=True)
    rollback_data = models.JSONField(
        null=True, blank=True,
        help_text='Snapshot of previous config for rollback'
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['policy_group', 'network_element']

    def __str__(self):
        return f'{self.policy_group} -> {self.network_element}'


class ComplianceAudit(models.Model):
    """Records compliance check results for NEs against policies."""

    class Result(models.TextChoices):
        COMPLIANT = 'COMPLIANT', 'Compliant'
        NON_COMPLIANT = 'NON_COMPLIANT', 'Non-Compliant'
        ERROR = 'ERROR', 'Error'
        SKIPPED = 'SKIPPED', 'Skipped'

    network_element = models.ForeignKey(
        'inventory.NetworkElement', on_delete=models.CASCADE,
        related_name='compliance_audits'
    )
    policy = models.ForeignKey(
        ConfigurationPolicy, on_delete=models.CASCADE,
        related_name='audits'
    )
    result = models.CharField(
        max_length=20, choices=Result.choices
    )
    expected_config = models.JSONField(
        help_text='Expected configuration from policy'
    )
    actual_config = models.JSONField(
        help_text='Actual configuration read from NE'
    )
    deviations = models.JSONField(
        default=list, help_text='List of specific deviations found'
    )
    audited_at = models.DateTimeField(default=timezone.now)
    audited_by = models.CharField(
        max_length=150, default='system',
        help_text='User or system that triggered audit'
    )

    class Meta:
        ordering = ['-audited_at']

    def __str__(self):
        return (
            f'Audit {self.network_element} vs '
            f'{self.policy}: {self.get_result_display()}'
        )


class ConfigurationSnapshot(models.Model):
    """Point-in-time snapshot of an NE full configuration."""

    network_element = models.ForeignKey(
        'inventory.NetworkElement', on_delete=models.CASCADE,
        related_name='config_snapshots'
    )
    config_data = models.JSONField(
        help_text='Full configuration dump from NE'
    )
    snapshot_type = models.CharField(
        max_length=30,
        choices=[
            ('SCHEDULED', 'Scheduled'),
            ('MANUAL', 'Manual'),
            ('PRE_CHANGE', 'Pre-Change'),
            ('POST_CHANGE', 'Post-Change'),
        ]
    )
    taken_at = models.DateTimeField(default=timezone.now)
    taken_by = models.CharField(max_length=150, default='system')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-taken_at']

    def __str__(self):
        return f'Snapshot {self.network_element} @ {self.taken_at}'


class FirmwarePolicy(models.Model):
    """Defines approved firmware versions per NE type."""

    ne_type = models.CharField(max_length=100)
    approved_version = models.CharField(max_length=50)
    minimum_version = models.CharField(max_length=50, blank=True)
    release_notes_url = models.URLField(blank=True)
    is_mandatory = models.BooleanField(default=False)
    deadline = models.DateTimeField(
        null=True, blank=True,
        help_text='Deadline for mandatory upgrade'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['ne_type', 'approved_version']
        verbose_name_plural = 'Firmware policies'

    def __str__(self):
        return f'{self.ne_type}: v{self.approved_version}'


class TimingSourcePriority(models.Model):
    """Configurable priority list for timing sources (Zero Trust)."""

    class SourceType(models.TextChoices):
        GNSS = 'GNSS', 'GNSS'
        CESIUM = 'CESIUM', 'Cesium PRS-4400'
        CSAC = 'CSAC', 'Chip-Scale Atomic Clock'
        RUBIDIUM = 'RUBIDIUM', 'Rubidium'
        OCXO = 'OCXO', 'OCXO'
        LEO_PNT = 'LEO_PNT', 'LEO Satellite (Xona/Satelles)'
        ELORAN = 'ELORAN', 'eLoran'
        WHITE_RABBIT = 'WHITE_RABBIT', 'White Rabbit'
        PTP_PEER = 'PTP_PEER', 'PTP Peer'
        NTP = 'NTP', 'NTP'
        OPTICAL_FIBER = 'OPTICAL_FIBER', 'Optical Fiber'

    network_element = models.ForeignKey(
        'inventory.NetworkElement', on_delete=models.CASCADE,
        related_name='timing_priorities'
    )
    source_type = models.CharField(
        max_length=20, choices=SourceType.choices
    )
    priority = models.PositiveIntegerField(
        help_text='Lower number = higher priority'
    )
    trust_threshold = models.FloatField(
        default=50.0,
        help_text='Minimum trust score (0-100) to use this source'
    )
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['network_element', 'priority']
        unique_together = ['network_element', 'source_type']

    def __str__(self):
        return (
            f'{self.network_element} - '
            f'{self.get_source_type_display()} (pri={self.priority})'
        )
