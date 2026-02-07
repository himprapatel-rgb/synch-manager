"""NTG App Serializers for DRF API"""
from rest_framework import serializers
from .models import (
    NTGNode, AtomicClock, CommonViewTimeTransfer,
    JammingEvent, SpoofingEvent, ClockStabilityTracking,
    AntennaEnvironment, PTPLinkEvaluation, TimingGridStatus
)


class NTGNodeSerializer(serializers.ModelSerializer):
    connected_clock_name = serializers.CharField(
        source='connected_atomic_clock.name', read_only=True
    )
    
    class Meta:
        model = NTGNode
        fields = '__all__'
        read_only_fields = ['id', 'installed_at', 'last_seen']


class AtomicClockSerializer(serializers.ModelSerializer):
    clock_type_display = serializers.CharField(
        source='get_clock_type_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = AtomicClock
        fields = '__all__'
        read_only_fields = ['id', 'installed_at']


class CVTTSerializer(serializers.ModelSerializer):
    node_a_name = serializers.CharField(source='node_a.name', read_only=True)
    node_b_name = serializers.CharField(source='node_b.name', read_only=True)
    pivot_clock_name = serializers.CharField(
        source='pivot_clock.name', read_only=True
    )
    
    class Meta:
        model = CommonViewTimeTransfer
        fields = '__all__'
        read_only_fields = ['id']


class JammingEventSerializer(serializers.ModelSerializer):
    node_name = serializers.CharField(source='node.name', read_only=True)
    severity_display = serializers.CharField(
        source='get_severity_display', read_only=True
    )
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = JammingEvent
        fields = '__all__'
        read_only_fields = ['id', 'detected_at']
    
    def get_duration_seconds(self, obj):
        if obj.ended_at:
            return (obj.ended_at - obj.detected_at).total_seconds()
        return None


class SpoofingEventSerializer(serializers.ModelSerializer):
    node_name = serializers.CharField(source='node.name', read_only=True)
    detection_method_display = serializers.CharField(
        source='get_detection_method_display', read_only=True
    )
    
    class Meta:
        model = SpoofingEvent
        fields = '__all__'
        read_only_fields = ['id', 'detected_at']


class ClockStabilitySerializer(serializers.ModelSerializer):
    clock_name = serializers.CharField(
        source='atomic_clock.name', read_only=True
    )
    
    class Meta:
        model = ClockStabilityTracking
        fields = '__all__'
        read_only_fields = ['id']


class AntennaEnvironmentSerializer(serializers.ModelSerializer):
    node_name = serializers.CharField(source='node.name', read_only=True)
    
    class Meta:
        model = AntennaEnvironment
        fields = '__all__'
        read_only_fields = ['id']


class PTPLinkEvaluationSerializer(serializers.ModelSerializer):
    gm_node_name = serializers.CharField(
        source='grandmaster_node.name', read_only=True
    )
    client_node_name = serializers.CharField(
        source='client_node.name', read_only=True
    )
    link_status_display = serializers.CharField(
        source='get_link_status_display', read_only=True
    )
    
    class Meta:
        model = PTPLinkEvaluation
        fields = '__all__'
        read_only_fields = ['id']


class TimingGridStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimingGridStatus
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']
