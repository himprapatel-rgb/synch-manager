"""
PTP Client Management Serializers for Synch-Manager.

IEEE 1588 PTP domains, grandmasters, clients, metrics,
topology links, and LinuxPTP instance serialization.
"""

from rest_framework import serializers

from .models import (
    PTPDomain, PTPGrandmaster, PTPClient, PTPClientMetrics,
    PTPTopologyLink, LinuxPTPInstance,
)


class PTPDomainSerializer(serializers.ModelSerializer):
    """Serializer for PTP domain groupings."""
    client_count = serializers.IntegerField(read_only=True)
    gm_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PTPDomain
        fields = [
            'id', 'domain_number', 'name', 'description',
            'profile', 'created_at', 'client_count', 'gm_count',
        ]
        read_only_fields = ['id', 'created_at']


class PTPGrandmasterSerializer(serializers.ModelSerializer):
    """Serializer for PTP grandmaster clocks."""
    client_count = serializers.SerializerMethodField()
    clock_class_display = serializers.CharField(
        source='get_clock_class_display', read_only=True,
    )

    class Meta:
        model = PTPGrandmaster
        fields = [
            'id', 'network_element', 'clock_identity', 'domain',
            'clock_class', 'clock_class_display', 'clock_accuracy',
            'priority1', 'priority2', 'time_source', 'two_step',
            'is_active', 'last_seen', 'client_count',
        ]
        read_only_fields = ['id']

    def get_client_count(self, obj):
        return obj.clients.count()


class PTPClientSerializer(serializers.ModelSerializer):
    """Serializer for PTP slave/client clocks."""
    port_state_display = serializers.CharField(
        source='get_port_state_display', read_only=True,
    )

    class Meta:
        model = PTPClient
        fields = [
            'id', 'hostname', 'ip_address', 'clock_identity',
            'port_state', 'port_state_display', 'grandmaster',
            'domain', 'ptp_implementation', 'transport',
            'is_monitored', 'discovered_at', 'last_seen',
        ]
        read_only_fields = ['id', 'discovered_at']


class PTPClientMetricsSerializer(serializers.ModelSerializer):
    """Serializer for PTP client time-series metrics."""

    class Meta:
        model = PTPClientMetrics
        fields = [
            'id', 'client', 'timestamp', 'offset_from_master_ns',
            'mean_path_delay_ns', 'frequency_offset_ppb',
            'port_state', 'gm_clock_identity', 'gm_clock_class',
            'steps_removed',
        ]
        read_only_fields = ['id']


class PTPTopologyLinkSerializer(serializers.ModelSerializer):
    """Serializer for PTP topology links between NEs."""
    link_type_display = serializers.CharField(
        source='get_link_type_display', read_only=True,
    )

    class Meta:
        model = PTPTopologyLink
        fields = [
            'id', 'source_ne', 'target_ne', 'link_type',
            'link_type_display', 'asymmetry_ns', 'is_active',
            'discovered_at', 'last_verified',
        ]
        read_only_fields = ['id', 'discovered_at']


class LinuxPTPInstanceSerializer(serializers.ModelSerializer):
    """Serializer for LinuxPTP (ptp4l/phc2sys) instances."""
    service_state_display = serializers.CharField(
        source='get_service_state_display', read_only=True,
    )

    class Meta:
        model = LinuxPTPInstance
        fields = [
            'id', 'client', 'ptp4l_config', 'phc2sys_config',
            'service_state', 'service_state_display',
            'ptp4l_version', 'interface',
            'hardware_timestamping', 'last_config_push',
        ]
        read_only_fields = ['id']
