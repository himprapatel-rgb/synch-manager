"""
DRF Serializers for Performance Management app.
"""

from rest_framework import serializers
from .models import PerformanceMetric, MTIEMask, SyncMeshScore, PerformanceThreshold


class PerformanceMetricSerializer(serializers.ModelSerializer):
    metric_type_display = serializers.CharField(
        source='get_metric_type_display', read_only=True,
    )
    network_element_name = serializers.CharField(
        source='network_element.name', read_only=True,
    )

    class Meta:
        model = PerformanceMetric
        fields = [
            'id', 'network_element', 'network_element_name',
            'metric_type', 'metric_type_display',
            'value', 'unit', 'timestamp',
            'interface_name', 'satellite_prn',
        ]
        read_only_fields = ['id']


class PerformanceMetricBulkSerializer(serializers.Serializer):
    """Accept a list of metrics for bulk ingestion from collectors."""
    metrics = PerformanceMetricSerializer(many=True)

    def create(self, validated_data):
        metrics_data = validated_data.pop('metrics')
        instances = [
            PerformanceMetric(**m) for m in metrics_data
        ]
        return PerformanceMetric.objects.bulk_create(instances)


class MTIEMaskSerializer(serializers.ModelSerializer):
    standard_display = serializers.CharField(
        source='get_standard_display', read_only=True,
    )

    class Meta:
        model = MTIEMask
        fields = [
            'id', 'name', 'standard', 'standard_display',
            'observation_interval_sec', 'mtie_limit_ns',
        ]


class SyncMeshScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncMeshScore
        fields = [
            'id', 'timestamp', 'overall_score',
            'gnss_health_score', 'ptp_accuracy_score',
            'wr_link_score', 'holdover_readiness_score',
            'peer_connectivity_score',
            'total_nodes', 'gnss_locked_nodes',
            'ptp_synced_nodes', 'holdover_nodes', 'failed_nodes',
            'war_mode_active',
        ]
        read_only_fields = ['id']


class PerformanceThresholdSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(
        source='get_severity_display', read_only=True,
    )
    metric_type_display = serializers.CharField(
        source='get_metric_type_display', read_only=True,
    )

    class Meta:
        model = PerformanceThreshold
        fields = [
            'id', 'name',
            'metric_type', 'metric_type_display',
            'upper_threshold', 'lower_threshold',
            'severity', 'severity_display',
            'enabled', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimeRangeQuerySerializer(serializers.Serializer):
    """Query parameters for time-series performance queries."""
    network_element = serializers.UUIDField(required=False)
    metric_type = serializers.ChoiceField(
        choices=PerformanceMetric.MetricType.choices,
        required=False,
    )
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)
    interval = serializers.ChoiceField(
        choices=[
            ('1m', '1 minute'),
            ('5m', '5 minutes'),
            ('15m', '15 minutes'),
            ('1h', '1 hour'),
            ('6h', '6 hours'),
            ('1d', '1 day'),
        ],
        required=False,
        default='5m',
    )
