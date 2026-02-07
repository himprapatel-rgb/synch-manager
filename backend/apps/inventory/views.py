"""
Synch-Manager Inventory Views

DRF ViewSets for Network Element CRUD, discovery, and topology.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import (
    NetworkElement, NetworkElementGroup, Card, Port, TimingLink
)
from .serializers import (
    NetworkElementListSerializer, NetworkElementDetailSerializer,
    NetworkElementGroupSerializer, CardSerializer, PortSerializer,
    TimingLinkSerializer, DiscoverySerializer
)


class NetworkElementGroupViewSet(viewsets.ModelViewSet):
    """CRUD for NE groups (logical containers for policy mgmt)."""
    queryset = NetworkElementGroup.objects.all()
    serializer_class = NetworkElementGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class NetworkElementViewSet(viewsets.ModelViewSet):
    """Full CRUD + discovery + status actions for Network Elements."""
    queryset = NetworkElement.objects.select_related('group').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]
    filterset_fields = [
        'ne_type', 'management_state', 'worst_alarm',
        'group', 'gnss_available'
    ]
    search_fields = ['name', 'ip_address', 'location_name', 'serial_number']
    ordering_fields = ['name', 'worst_alarm', 'trust_score', 'last_polled']

    def get_serializer_class(self):
        if self.action == 'list':
            return NetworkElementListSerializer
        return NetworkElementDetailSerializer

    @action(detail=True, methods=['post'])
    def discover(self, request, pk=None):
        """Trigger SNMP discovery for a single NE."""
        ne = self.get_object()
        serializer = DiscoverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # In production this would dispatch a Celery task
        ne.last_discovered = timezone.now()
        ne.save(update_fields=['last_discovered'])
        return Response(
            {'status': 'discovery_started', 'ne_id': ne.id},
            status=status.HTTP_202_ACCEPTED
        )

    @action(detail=True, methods=['post'])
    def manage(self, request, pk=None):
        """Set NE to MANAGED state."""
        ne = self.get_object()
        ne.management_state = 'MANAGED'
        ne.save(update_fields=['management_state'])
        return Response({'status': 'managed', 'ne_id': ne.id})

    @action(detail=True, methods=['post'])
    def unmanage(self, request, pk=None):
        """Set NE to UNMANAGED state."""
        ne = self.get_object()
        ne.management_state = 'UNMANAGED'
        ne.save(update_fields=['management_state'])
        return Response({'status': 'unmanaged', 'ne_id': ne.id})

    @action(detail=False, methods=['get'])
    def war_mode_status(self, request):
        """Return War Mode dashboard data: GNSS availability across all NEs."""
        total = NetworkElement.objects.filter(
            management_state='MANAGED'
        ).count()
        gnss_down = NetworkElement.objects.filter(
            management_state='MANAGED', gnss_available=False
        ).count()
        threshold = 0.5  # 50% triggers War Mode
        war_mode_active = (
            total > 0 and (gnss_down / total) >= threshold
        )
        holdover_nodes = NetworkElement.objects.filter(
            management_state='MANAGED',
            gnss_available=False,
            holdover_estimate_hours__isnull=False
        ).values('id', 'name', 'oscillator_type', 'holdover_estimate_hours')
        return Response({
            'war_mode_active': war_mode_active,
            'total_managed': total,
            'gnss_down_count': gnss_down,
            'gnss_down_percent': round(
                (gnss_down / total * 100) if total else 0, 1
            ),
            'holdover_nodes': list(holdover_nodes),
        })

    @action(detail=False, methods=['get'])
    def trust_overview(self, request):
        """Zero Trust overview: trust scores across the network."""
        from django.db.models import Avg, Min, Count, Q
        stats = NetworkElement.objects.filter(
            management_state='MANAGED'
        ).aggregate(
            avg_trust=Avg('trust_score'),
            min_trust=Min('trust_score'),
            low_trust_count=Count(
                'id', filter=Q(trust_score__lt=50)
            ),
            total=Count('id')
        )
        return Response(stats)


class CardViewSet(viewsets.ModelViewSet):
    """CRUD for cards/modules within NEs."""
    queryset = Card.objects.select_related('network_element').all()
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['network_element', 'operational_state']


class PortViewSet(viewsets.ModelViewSet):
    """CRUD for ports on cards."""
    queryset = Port.objects.select_related(
        'card', 'card__network_element'
    ).all()
    serializer_class = PortSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'card', 'port_type', 'direction',
        'operational_state', 'admin_state'
    ]


class TimingLinkViewSet(viewsets.ModelViewSet):
    """CRUD for timing distribution links (topology)."""
    queryset = TimingLink.objects.select_related(
        'source_port__card__network_element',
        'destination_port__card__network_element'
    ).all()
    serializer_class = TimingLinkSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['link_type', 'is_active']
