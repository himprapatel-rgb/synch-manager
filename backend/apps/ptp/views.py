"""
PTP Client Management Views for Synch-Manager.

PTP domains, grandmasters, clients, metrics, topology links,
and LinuxPTP instance management.
"""

from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers as drf_serializers
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    PTPDomain, PTPGrandmaster, PTPClient, PTPClientMetrics,
    PTPTopologyLink, LinuxPTPInstance,
)


# --- Serializers ---


class PTPDomainSerializer(drf_serializers.ModelSerializer):
    client_count = drf_serializers.IntegerField(read_only=True)
    gm_count = drf_serializers.IntegerField(read_only=True)

    class Meta:
        model = PTPDomain
        fields = '__all__'


class PTPGrandmasterSerializer(drf_serializers.ModelSerializer):
    client_count = drf_serializers.SerializerMethodField()

    class Meta:
        model = PTPGrandmaster
        fields = '__all__'

    def get_client_count(self, obj):
        return obj.clients.count()


class PTPClientSerializer(drf_serializers.ModelSerializer):
    port_state_display = drf_serializers.CharField(
        source='get_port_state_display', read_only=True,
    )

    class Meta:
        model = PTPClient
        fields = '__all__'


class PTPClientMetricsSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = PTPClientMetrics
        fields = '__all__'


class PTPTopologyLinkSerializer(drf_serializers.ModelSerializer):
    link_type_display = drf_serializers.CharField(
        source='get_link_type_display', read_only=True,
    )

    class Meta:
        model = PTPTopologyLink
        fields = '__all__'


class LinuxPTPInstanceSerializer(drf_serializers.ModelSerializer):
    service_state_display = drf_serializers.CharField(
        source='get_service_state_display', read_only=True,
    )

    class Meta:
        model = LinuxPTPInstance
        fields = '__all__'


# --- ViewSets ---


class PTPDomainViewSet(viewsets.ModelViewSet):
    """Manage PTP domains."""

    queryset = PTPDomain.objects.annotate(
        client_count=Count('clients'),
        gm_count=Count('grandmasters'),
    )
    serializer_class = PTPDomainSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PTPGrandmasterViewSet(viewsets.ModelViewSet):
    """Manage PTP grandmaster clocks."""

    queryset = PTPGrandmaster.objects.select_related(
        'network_element', 'domain'
    ).all()
    serializer_class = PTPGrandmasterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain', 'clock_class', 'is_active', 'time_source']


class PTPClientViewSet(viewsets.ModelViewSet):
    """Manage PTP clients."""

    queryset = PTPClient.objects.select_related(
        'grandmaster', 'domain'
    ).all()
    serializer_class = PTPClientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'port_state', 'grandmaster', 'domain',
        'ptp_implementation', 'is_monitored',
    ]

    @action(detail=True, methods=['get'], url_path='metrics')
    def get_metrics(self, request, pk=None):
        """Get recent metrics for a PTP client."""
        client = self.get_object()
        limit = int(request.query_params.get('limit', 100))
        metrics = PTPClientMetrics.objects.filter(
            client=client
        ).order_by('-timestamp')[:limit]
        return Response(
            PTPClientMetricsSerializer(metrics, many=True).data
        )

    @action(detail=True, methods=['get'], url_path='metrics/summary')
    def metrics_summary(self, request, pk=None):
        """Get aggregated metrics summary for a PTP client."""
        client = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timezone.timedelta(hours=hours)
        stats = PTPClientMetrics.objects.filter(
            client=client, timestamp__gte=since
        ).aggregate(
            avg_offset=Avg('offset_from_master_ns'),
            max_offset=Max('offset_from_master_ns'),
            min_offset=Min('offset_from_master_ns'),
            avg_delay=Avg('mean_path_delay_ns'),
            max_delay=Max('mean_path_delay_ns'),
            sample_count=Count('id'),
        )
        return Response({
            'client_id': client.id,
            'period_hours': hours,
            **stats,
        })

    @action(detail=False, methods=['get'], url_path='sync-loss')
    def sync_loss_clients(self, request):
        """List clients that have lost sync (not in SLAVE state)."""
        problem_clients = self.queryset.exclude(
            port_state=PTPClient.PortState.SLAVE
        ).filter(is_monitored=True)
        return Response(
            PTPClientSerializer(problem_clients, many=True).data
        )


class PTPClientMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to PTP client metrics."""

    queryset = PTPClientMetrics.objects.select_related('client').all()
    serializer_class = PTPClientMetricsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'port_state']


class PTPTopologyLinkViewSet(viewsets.ModelViewSet):
    """Manage PTP topology links between NEs."""

    queryset = PTPTopologyLink.objects.select_related(
        'source_ne', 'target_ne'
    ).all()
    serializer_class = PTPTopologyLinkSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['link_type', 'is_active', 'source_ne', 'target_ne']

    @action(detail=False, methods=['get'], url_path='graph')
    def topology_graph(self, request):
        """Return topology as nodes and edges for visualization."""
        links = self.queryset.filter(is_active=True)
        nodes = set()
        edges = []
        for link in links:
            nodes.add(link.source_ne_id)
            nodes.add(link.target_ne_id)
            edges.append({
                'source': link.source_ne_id,
                'target': link.target_ne_id,
                'type': link.link_type,
                'asymmetry_ns': link.asymmetry_ns,
            })
        return Response({
            'nodes': list(nodes),
            'edges': edges,
        })


class LinuxPTPInstanceViewSet(viewsets.ModelViewSet):
    """Manage LinuxPTP (ptp4l/phc2sys) instances."""

    queryset = LinuxPTPInstance.objects.select_related('client').all()
    serializer_class = LinuxPTPInstanceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['service_state', 'hardware_timestamping']

    @action(detail=True, methods=['post'], url_path='push-config')
    def push_config(self, request, pk=None):
        """Push ptp4l/phc2sys configuration to a host."""
        instance = self.get_object()
        new_config = request.data.get('ptp4l_config')
        if new_config:
            instance.ptp4l_config = new_config
        phc_config = request.data.get('phc2sys_config')
        if phc_config:
            instance.phc2sys_config = phc_config
        instance.last_config_push = timezone.now()
        instance.save()
        return Response(LinuxPTPInstanceSerializer(instance).data)

    @action(detail=True, methods=['post'], url_path='restart')
    def restart_service(self, request, pk=None):
        """Restart ptp4l/phc2sys service on remote host."""
        instance = self.get_object()
        # Placeholder: actual SSH-based restart in Celery task
        instance.service_state = LinuxPTPInstance.ServiceState.RUNNING
        instance.save(update_fields=['service_state'])
        return Response({
            'status': 'restart_initiated',
            'instance': LinuxPTPInstanceSerializer(instance).data,
        })
