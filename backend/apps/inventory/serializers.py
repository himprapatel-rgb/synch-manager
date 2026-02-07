"""
Synch-Manager Inventory Serializers

DRF serializers for Network Element, Card, Port, and TimingLink.
"""

from rest_framework import serializers
from .models import (
    NetworkElement, NetworkElementGroup, Card, Port, TimingLink
)


class NetworkElementGroupSerializer(serializers.ModelSerializer):
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = NetworkElementGroup
        fields = [
            'id', 'name', 'description', 'parent',
            'children_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_children_count(self, obj):
        return obj.children.count()


class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = [
            'id', 'card', 'port_number', 'port_type', 'direction',
            'admin_state', 'operational_state', 'signal_quality',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CardSerializer(serializers.ModelSerializer):
    ports = PortSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 'network_element', 'slot', 'card_type',
            'part_number', 'serial_number', 'firmware_version',
            'operational_state', 'ports', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class NetworkElementListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    ne_type_display = serializers.CharField(
        source='get_ne_type_display', read_only=True
    )
    group_name = serializers.CharField(
        source='group.name', read_only=True, default=''
    )
    active_alarms = serializers.SerializerMethodField()

    class Meta:
        model = NetworkElement
        fields = [
            'id', 'name', 'ne_type', 'ne_type_display',
            'ip_address', 'management_state', 'worst_alarm',
            'group', 'group_name', 'location_name',
            'trust_score', 'gnss_available', 'active_alarms',
            'last_polled', 'created_at'
        ]

    def get_active_alarms(self, obj):
        if hasattr(obj, 'alarms'):
            return obj.alarms.filter(state='ACTIVE').count()
        return 0


class NetworkElementDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail/create/update views."""
    ne_type_display = serializers.CharField(
        source='get_ne_type_display', read_only=True
    )
    cards = CardSerializer(many=True, read_only=True)
    group_name = serializers.CharField(
        source='group.name', read_only=True, default=''
    )

    class Meta:
        model = NetworkElement
        fields = [
            'id', 'name', 'ne_type', 'ne_type_display',
            'ip_address', 'snmp_community', 'snmp_version',
            'management_state', 'worst_alarm',
            'group', 'group_name',
            'location_lat', 'location_lon', 'location_name',
            'sys_descr', 'sys_object_id',
            'firmware_version', 'serial_number', 'hardware_revision',
            'last_discovered', 'last_polled', 'uptime_seconds',
            'notes', 'trust_score', 'oscillator_type',
            'gnss_available', 'holdover_start', 'holdover_estimate_hours',
            'cards', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'worst_alarm', 'sys_descr', 'sys_object_id',
            'firmware_version', 'serial_number', 'hardware_revision',
            'last_discovered', 'last_polled', 'uptime_seconds',
            'trust_score', 'holdover_start', 'holdover_estimate_hours',
            'created_at', 'updated_at'
        ]


class TimingLinkSerializer(serializers.ModelSerializer):
    source_ne = serializers.CharField(
        source='source_port.card.network_element.name', read_only=True
    )
    dest_ne = serializers.CharField(
        source='destination_port.card.network_element.name', read_only=True
    )

    class Meta:
        model = TimingLink
        fields = [
            'id', 'source_port', 'destination_port',
            'source_ne', 'dest_ne',
            'link_type', 'estimated_delay_ns',
            'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class DiscoverySerializer(serializers.Serializer):
    """Serializer for triggering NE discovery."""
    force = serializers.BooleanField(
        default=False,
        help_text='Force full re-discovery even if recently discovered'
    )
