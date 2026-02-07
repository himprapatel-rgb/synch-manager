"""
DRF Views for Performance Management app.

Provides REST endpoints for querying time-series performance data,
MTIE/TDEV compliance, Sync Mesh Score, and threshold management.
"""

from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    PerformanceMetric, MTIEMask, SyncMeshScore, PerformanceThreshold,
)
from .serializers import (
    PerformanceMetricSerializer,
    PerformanceMetricBulkSerializer,
    MTIEMaskSerializer,
    SyncMeshScoreSerializer,
    PerformanceThresholdSerializer,
    TimeRangeQuerySerializer,
)


class PerformanceMetricViewSet(viewsets.ModelViewSet):
    """CRUD + time-range queries for performance metrics."""
    queryset = PerformanceMetric.objects.select_related('network_element')
    serializer_class = PerformanceMetricSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['network_element', 'metric_type']

    def get_queryset(self):
        qs = super().get_queryset()
        # Default to last 24 hours if no time filter
        start = self.request.query_params.get('start_time')
        end = self.request.query_params.get('end_time')
        if not start:
            qs = qs.filter(timestamp__gte=timezone.now() - timedelta(hours=24))
        else:
            qs = qs.filter(timestamp__gte=start)
        if end:
            qs = qs.filter(timestamp__lte=end)
        return qs

    @action(detail=False, methods=['post'], url_path='bulk-ingest')
    def bulk_ingest(self, request):
        """Bulk ingest metrics from collectors/pollers."""
        serializer = PerformanceMetricBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()
        return Response(
            {'ingested': len(instances)},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'], url_path='by-element/(?P<element_id>[^/.]+)')
    def by_element(self, request, element_id=None):
        """Get all metrics for a specific network element."""
        qs = self.get_queryset().filter(network_element_id=element_id)
        metric_type = request.query_params.get('metric_type')
        if metric_type:
            qs = qs.filter(metric_type=metric_type)
        serializer = self.get_serializer(qs[:1000], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='mtie-compliance/(?P<element_id>[^/.]+)')
    def mtie_compliance(self, request, element_id=None):
        """Check MTIE compliance against ITU-T masks."""
        standard = request.query_params.get('standard', 'G8275_1')
        masks = MTIEMask.objects.filter(standard=standard)
        metrics = self.get_queryset().filter(
            network_element_id=element_id,
            metric_type='MTIE',
        ).order_by('timestamp')

        violations = []
        for mask in masks:
            exceeding = metrics.filter(
                value__gt=mask.mtie_limit_ns,
            )
            if exceeding.exists():
                violations.append({
                    'tau': mask.observation_interval_sec,
                    'limit_ns': mask.mtie_limit_ns,
                    'violation_count': exceeding.count(),
                    'max_value_ns': exceeding.order_by('-value').first().value,
                })

        return Response({
            'element_id': element_id,
            'standard': standard,
            'compliant': len(violations) == 0,
            'violations': violations,
        })


class SyncMeshScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """Network-wide synchronization health scores."""
    queryset = SyncMeshScore.objects.all()
    serializer_class = SyncMeshScoreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'], url_path='current')
    def current(self, request):
        """Get the most recent Sync Mesh Score."""
        latest = SyncMeshScore.objects.first()
        if not latest:
            return Response(
                {'detail': 'No scores computed yet'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(latest)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='trend')
    def trend(self, request):
        """Get score trend for the last N hours."""
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        scores = SyncMeshScore.objects.filter(timestamp__gte=since)
        serializer = self.get_serializer(scores, many=True)
        return Response(serializer.data)


class MTIEMaskViewSet(viewsets.ReadOnlyModelViewSet):
    """ITU-T MTIE compliance mask definitions."""
    queryset = MTIEMask.objects.all()
    serializer_class = MTIEMaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['standard']


class PerformanceThresholdViewSet(viewsets.ModelViewSet):
    """CRUD for performance alarm thresholds."""
    queryset = PerformanceThreshold.objects.all()
    serializer_class = PerformanceThresholdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['metric_type', 'severity', 'enabled']
