"""Auto-register all app models in Django Admin."""
from django.contrib import admin

# Fault app models
from apps.fault.models import Alarm, Event, AlarmPolicy

# Configuration app models
from apps.configuration.models import (
    SyncPolicy, PolicyGroup, ComplianceAudit,
    FirmwareImage, ConfigSnapshot, ZeroTrustSource
)

# Performance app models
from apps.performance.models import (
    PerformanceMetric, SyncMeshScore, MTIEMask, PerformanceThreshold
)

# Security app models
from apps.security.models import GNSSStatus, ThreatEvent, WarModeEvent, AuditLog

# PTP app models
from apps.ptp.models import (
    PTPDomain, PTPGrandmaster, PTPClient,
    PTPMetric, PTPTopologyLink, LinuxPTPConfig
)

# War Mode app models
from apps.war_mode.models import (
    WarModeSession, WarModeTransition, WarModeFailover,
    HoldoverStatus, PTPWarDomain, CSACStatus
)

# NTG app models
from apps.ntg.models import (
    NTGNode, AtomicClock, CVTTSession, JammingEvent,
    SpoofingEvent, ClockStability, AntennaEnvironment,
    PTPLinkEvaluation, GridStatus
)


# Register Fault models
@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = ['alarm_id', 'network_element', 'severity', 'state', 'raised_at']
    list_filter = ['severity', 'state', 'category']
    search_fields = ['alarm_id', 'description']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'event_type', 'severity', 'timestamp']
    list_filter = ['event_type', 'severity']

@admin.register(AlarmPolicy)
class AlarmPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'severity_filter', 'is_active']
    list_filter = ['is_active']


# Register Configuration models
@admin.register(SyncPolicy)
class SyncPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'policy_type', 'version', 'is_active']
    list_filter = ['policy_type', 'is_active']

@admin.register(PolicyGroup)
class PolicyGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']

@admin.register(ComplianceAudit)
class ComplianceAuditAdmin(admin.ModelAdmin):
    list_display = ['policy', 'status', 'run_at']
    list_filter = ['status']

@admin.register(FirmwareImage)
class FirmwareImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'ne_type', 'uploaded_at']

@admin.register(ConfigSnapshot)
class ConfigSnapshotAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'created_at', 'label']

@admin.register(ZeroTrustSource)
class ZeroTrustSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'trust_score', 'is_active']
    list_filter = ['source_type', 'is_active']


# Register Performance models
@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'metric_type', 'value', 'timestamp']
    list_filter = ['metric_type']

@admin.register(SyncMeshScore)
class SyncMeshScoreAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'score', 'calculated_at']

@admin.register(MTIEMask)
class MTIEMaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'standard']

@admin.register(PerformanceThreshold)
class PerformanceThresholdAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'warning_threshold', 'critical_threshold']


# Register Security models
@admin.register(GNSSStatus)
class GNSSStatusAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'constellation', 'satellites_tracked', 'fix_type']
    list_filter = ['constellation', 'fix_type']

@admin.register(ThreatEvent)
class ThreatEventAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'threat_type', 'severity', 'detected_at']
    list_filter = ['threat_type', 'severity']

@admin.register(WarModeEvent)
class WarModeEventAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'event_type', 'timestamp']
    list_filter = ['event_type']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'timestamp']
    list_filter = ['action', 'resource_type']


# Register PTP models
@admin.register(PTPDomain)
class PTPDomainAdmin(admin.ModelAdmin):
    list_display = ['domain_number', 'profile', 'name']
    list_filter = ['profile']

@admin.register(PTPGrandmaster)
class PTPGrandmasterAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'domain', 'clock_class', 'clock_accuracy']

@admin.register(PTPClient)
class PTPClientAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'domain', 'grandmaster', 'sync_state']
    list_filter = ['sync_state']

@admin.register(PTPMetric)
class PTPMetricAdmin(admin.ModelAdmin):
    list_display = ['client', 'offset_ns', 'path_delay_ns', 'timestamp']

@admin.register(PTPTopologyLink)
class PTPTopologyLinkAdmin(admin.ModelAdmin):
    list_display = ['source_element', 'destination_element', 'domain', 'link_type']

@admin.register(LinuxPTPConfig)
class LinuxPTPConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'ptp4l_profile', 'created_at']


# Register War Mode models
@admin.register(WarModeSession)
class WarModeSessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'activated_at', 'deactivated_at']
    list_filter = ['status']

@admin.register(WarModeTransition)
class WarModeTransitionAdmin(admin.ModelAdmin):
    list_display = ['session', 'from_state', 'to_state', 'timestamp']

@admin.register(WarModeFailover)
class WarModeFailoverAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'session', 'failover_type', 'timestamp']

@admin.register(HoldoverStatus)
class HoldoverStatusAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'oscillator_type', 'estimated_hours', 'entered_at']

@admin.register(PTPWarDomain)
class PTPWarDomainAdmin(admin.ModelAdmin):
    list_display = ['session', 'domain', 'is_isolated']

@admin.register(CSACStatus)
class CSACStatusAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'frequency_accuracy', 'temperature', 'updated_at']


# Register NTG models
@admin.register(NTGNode)
class NTGNodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'node_type', 'status', 'location']
    list_filter = ['node_type', 'status']

@admin.register(AtomicClock)
class AtomicClockAdmin(admin.ModelAdmin):
    list_display = ['node', 'clock_type', 'manufacturer', 'status']
    list_filter = ['clock_type', 'status']

@admin.register(CVTTSession)
class CVTTSessionAdmin(admin.ModelAdmin):
    list_display = ['source_node', 'target_node', 'status', 'started_at']

@admin.register(JammingEvent)
class JammingEventAdmin(admin.ModelAdmin):
    list_display = ['node', 'severity', 'detected_at', 'resolved_at']
    list_filter = ['severity']

@admin.register(SpoofingEvent)
class SpoofingEventAdmin(admin.ModelAdmin):
    list_display = ['node', 'severity', 'detected_at', 'resolved_at']
    list_filter = ['severity']

@admin.register(ClockStability)
class ClockStabilityAdmin(admin.ModelAdmin):
    list_display = ['clock', 'adev_1s', 'adev_100s', 'measured_at']

@admin.register(AntennaEnvironment)
class AntennaEnvironmentAdmin(admin.ModelAdmin):
    list_display = ['node', 'sky_visibility', 'multipath_risk', 'updated_at']

@admin.register(PTPLinkEvaluation)
class PTPLinkEvaluationAdmin(admin.ModelAdmin):
    list_display = ['source_node', 'target_node', 'quality_score', 'evaluated_at']

@admin.register(GridStatus)
class GridStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'overall_health', 'node_count', 'updated_at']
