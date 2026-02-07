"""
Security & GNSS Resilience Serializers for Synch-Manager.

DRF serializers for GNSS status, threat events, War Mode state,
and tamper-evident audit logging.
"""

from rest_framework import serializers
from .models import GNSSStatus, ThreatEvent, WarModeState, AuditLogEntry


class GNSSStatusSerializer(serializers.ModelSerializer):
    time_source_display = serializers.CharField(
        source='get_time_source_display', read_only=True,
    )

    class Meta:
        model = GNSSStatus
        fields = [
            'id', 'network_element', 'gnss_locked', 'satellites_tracked',
            'c_no_avg_dbhz', 'position_lat', 'position_lon',
            'time_source', 'time_source_display', 'trust_score',
            'spoofing_detected', 'jamming_detected', 'osnma_authenticated',
            'holdover_elapsed_sec', 'last_updated',
        ]
        read_only_fields = ['id', 'last_updated']


class ThreatEventSerializer(serializers.ModelSerializer):
    threat_type_display = serializers.CharField(
        source='get_threat_type_display', read_only=True,
    )
    severity_display = serializers.CharField(
        source='get_severity_display', read_only=True,
    )

    class Meta:
        model = ThreatEvent
        fields = [
            'id', 'network_element', 'threat_type', 'threat_type_display',
            'severity', 'severity_display', 'description',
            'detected_at', 'resolved_at', 'resolved', 'evidence',
        ]
        read_only_fields = ['id', 'detected_at']


class WarModeStateSerializer(serializers.ModelSerializer):
    state_display = serializers.CharField(
        source='get_current_state_display', read_only=True,
    )

    class Meta:
        model = WarModeState
        fields = [
            'id', 'current_state', 'state_display', 'activated_at',
            'activated_by', 'reason', 'gnss_denied_count',
            'total_node_count', 'last_state_change',
        ]
        read_only_fields = ['id', 'last_state_change']


class AuditLogEntrySerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(
        source='get_event_type_display', read_only=True,
    )

    class Meta:
        model = AuditLogEntry
        fields = [
            'id', 'event_type', 'event_type_display',
            'network_element', 'timestamp', 'actor',
            'details', 'previous_hash', 'entry_hash',
        ]
        read_only_fields = ['id', 'timestamp', 'previous_hash', 'entry_hash']
