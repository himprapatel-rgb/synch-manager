"""
Synch-Manager Fault Management Serializers

Alarm, Event, and AlarmPolicy serializers following ITU-T X.733/X.734
alarm standards for synchronization network fault management.
"""

from rest_framework import serializers

from .models import Alarm, Event, AlarmPolicy


class AlarmSerializer(serializers.ModelSerializer):
    """Serializer for active and historical alarms."""
    ne_name = serializers.CharField(
        source='network_element.name', read_only=True,
    )
    severity_display = serializers.CharField(
        source='get_severity_display', read_only=True,
    )
    state_display = serializers.CharField(
        source='get_state_display', read_only=True,
    )
    category_display = serializers.CharField(
        source='get_category_display', read_only=True,
    )

    class Meta:
        model = Alarm
        fields = [
            'id', 'network_element', 'ne_name',
            'alarm_type', 'severity', 'severity_display',
            'state', 'state_display',
            'category', 'category_display',
            'probable_cause', 'description', 'additional_info',
            'managed_object', 'trap_oid', 'trap_varbinds',
            'is_gnss_related', 'trust_impact',
            'raised_at', 'acknowledged_at', 'cleared_at',
            'acknowledged_by', 'ack_comment',
        ]
        read_only_fields = [
            'id', 'raised_at', 'acknowledged_at',
            'cleared_at', 'acknowledged_by',
        ]


class EventSerializer(serializers.ModelSerializer):
    """Serializer for informational event log entries."""
    ne_name = serializers.CharField(
        source='network_element.name', read_only=True,
        default='SYSTEM',
    )
    severity_display = serializers.CharField(
        source='get_severity_display', read_only=True,
    )

    class Meta:
        model = Event
        fields = [
            'id', 'network_element', 'ne_name', 'source',
            'event_type', 'severity', 'severity_display',
            'description', 'details', 'timestamp',
        ]
        read_only_fields = ['id', 'timestamp']


class AlarmPolicySerializer(serializers.ModelSerializer):
    """Serializer for alarm suppression, escalation, and forwarding rules."""

    class Meta:
        model = AlarmPolicy
        fields = [
            'id', 'name', 'description', 'is_active',
            'match_ne_type', 'match_alarm_type',
            'match_severity', 'match_category',
            'action', 'action_params',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AlarmAckSerializer(serializers.Serializer):
    """Serializer for alarm acknowledgment requests."""
    comment = serializers.CharField(required=False, default='')
