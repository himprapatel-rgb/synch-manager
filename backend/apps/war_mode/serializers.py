"""
War Mode Serializers for Synch-Manager.

DRF serializers for war mode sessions, transitions,
timing source failovers, holdover events, tactical domains,
and CSAC status.
"""

from rest_framework import serializers
from .models import (
    WarModeSession, WarModeTransition, TimingSourceFailover,
    HoldoverEvent, TacticalDomain, CSACStatus,
)


class WarModeTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarModeTransition
        fields = [
            'id', 'session', 'from_level', 'to_level',
            'threat_indicators', 'transitioned_at',
        ]
        read_only_fields = ['id', 'transitioned_at']


class WarModeSessionSerializer(serializers.ModelSerializer):
    transitions = WarModeTransitionSerializer(many=True, read_only=True)
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = WarModeSession
        fields = [
            'id', 'level', 'threat_type', 'activated_at',
            'deactivated_at', 'is_active', 'activated_by',
            'reason', 'threat_indicators', 'transitions',
            'duration_seconds',
        ]
        read_only_fields = ['id', 'activated_at']

    def get_duration_seconds(self, obj):
        if obj.deactivated_at and obj.activated_at:
            return (obj.deactivated_at - obj.activated_at).total_seconds()
        return None


class TimingSourceFailoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimingSourceFailover
        fields = [
            'id', 'network_element', 'session', 'from_source',
            'to_source', 'reason', 'switched_at',
            'switchover_duration_ms',
        ]
        read_only_fields = ['id', 'switched_at']


class HoldoverEventSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = HoldoverEvent
        fields = [
            'id', 'network_element', 'session', 'oscillator_type',
            'quality', 'drift_rate_ppb', 'started_at', 'ended_at',
            'is_active', 'total_drift_ns', 'duration_seconds',
        ]
        read_only_fields = ['id', 'started_at']

    def get_duration_seconds(self, obj):
        if obj.ended_at and obj.started_at:
            return (obj.ended_at - obj.started_at).total_seconds()
        return None


class TacticalDomainSerializer(serializers.ModelSerializer):
    ne_count = serializers.SerializerMethodField()

    class Meta:
        model = TacticalDomain
        fields = [
            'id', 'name', 'description', 'network_elements',
            'sync_mesh_enabled', 'emcon_active', 'current_level',
            'created_at', 'updated_at', 'ne_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_ne_count(self, obj):
        return obj.network_elements.count()


class CSACStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSACStatus
        fields = [
            'id', 'network_element', 'is_active', 'is_ready',
            'temperature_c', 'power_watts', 'allan_deviation',
            'drift_rate_per_day', 'activated_at', 'last_updated',
        ]
        read_only_fields = ['id', 'last_updated']


class WarModeActivateSerializer(serializers.Serializer):
    """Serializer for activating war mode."""
    level = serializers.ChoiceField(
        choices=['PEACETIME', 'ELEVATED', 'TACTICAL', 'CRITICAL', 'HOLDOVER'],
    )
    threat_type = serializers.ChoiceField(
        choices=['BENIGN', 'JAMMING', 'SPOOFING', 'KINETIC', 'CYBER', 'EMP', 'MULTI_DOMAIN'],
        default='BENIGN',
    )
    reason = serializers.CharField(required=False, default='')
    threat_indicators = serializers.JSONField(required=False, default=dict)


class TacticalStatusSerializer(serializers.Serializer):
    """Read-only serializer for tactical timing dashboard."""
    active_sessions = serializers.IntegerField()
    total_domains = serializers.IntegerField()
    domains_in_war_mode = serializers.IntegerField()
    active_holdovers = serializers.IntegerField()
    recent_failovers = serializers.IntegerField()
    sync_mesh_domains = serializers.IntegerField()
    emcon_domains = serializers.IntegerField()
