"""
Synch-Manager Fault Management Views

ViewSets for Alarm CRUD, acknowledge, clear, and Event log.
Includes inline serializers.
"""

from rest_framework import viewsets, serializers, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count, Q

from .models import Alarm, Event, AlarmPolicy


# --- Serializers ---

class AlarmSerializer(serializers.ModelSerializer):
    ne_name = serializers.CharField(
        source='network_element.name', read_only=True
    )

    class Meta:
        model = Alarm
        fields = [
            'id', 'network_element', 'ne_name',
            'alarm_type', 'severity', 'state', 'category',
            'probable_cause', 'description', 'additional_info',
            'managed_object', 'trap_oid',
            'is_gnss_related', 'trust_impact',
            'raised_at', 'acknowledged_at', 'cleared_at',
            'acknowledged_by', 'ack_comment'
        ]
        read_only_fields = [
            'raised_at', 'acknowledged_at', 'cleared_at',
            'acknowledged_by'
        ]


class EventSerializer(serializers.ModelSerializer):
    ne_name = serializers.CharField(
        source='network_element.name', read_only=True,
        default='SYSTEM'
    )

    class Meta:
        model = Event
        fields = [
            'id', 'network_element', 'ne_name',
            'source', 'event_type', 'severity',
            'description', 'details', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class AlarmPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = AlarmPolicy
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AlarmAckSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, default='')


# --- ViewSets ---

class AlarmViewSet(viewsets.ModelViewSet):
    """Full alarm management: list, filter, acknowledge, clear."""
    queryset = Alarm.objects.select_related('network_element').all()
    serializer_class = AlarmSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]
    filterset_fields = [
        'severity', 'state', 'category',
        'network_element', 'is_gnss_related'
    ]
    search_fields = ['alarm_type', 'description', 'network_element__name']
    ordering_fields = ['raised_at', 'severity', 'state']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """List only active alarms."""
        qs = self.get_queryset().filter(state='ACTIVE')
        qs = self.filter_queryset(qs)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def ack(self, request, pk=None):
        """Acknowledge an alarm."""
        alarm = self.get_object()
        ser = AlarmAckSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        alarm.state = 'ACKNOWLEDGED'
        alarm.acknowledged_at = timezone.now()
        alarm.acknowledged_by = request.user
        alarm.ack_comment = ser.validated_data.get('comment', '')
        alarm.save()
        return Response(AlarmSerializer(alarm).data)

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Clear an alarm."""
        alarm = self.get_object()
        alarm.state = 'CLEARED'
        alarm.cleared_at = timezone.now()
        alarm.save()
        return Response(AlarmSerializer(alarm).data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Alarm severity summary across the network."""
        stats = Alarm.objects.filter(state='ACTIVE').values(
            'severity'
        ).annotate(count=Count('id')).order_by('severity')
        gnss_active = Alarm.objects.filter(
            state='ACTIVE', is_gnss_related=True
        ).count()
        return Response({
            'by_severity': list(stats),
            'gnss_related_active': gnss_active,
            'total_active': Alarm.objects.filter(state='ACTIVE').count()
        })


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only event log."""
    queryset = Event.objects.select_related('network_element').all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]
    filterset_fields = ['source', 'severity', 'network_element']
    search_fields = ['event_type', 'description']
    ordering_fields = ['timestamp', 'severity']


class AlarmPolicyViewSet(viewsets.ModelViewSet):
    """CRUD for alarm policies."""
    queryset = AlarmPolicy.objects.all()
    serializer_class = AlarmPolicySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'action']

    
class GNSSAlarmSummaryViewSet(viewsets.ViewSet):
    """GNSS alarm summary: counts by severity for GNSS-related alarms."""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs = Alarm.objects.filter(is_gnss_related=True)
        active = qs.filter(state='ACTIVE')
        by_severity = list(
            active.values('severity').annotate(
                count=Count('id')
            ).order_by('severity')
        )
        return Response({
            'total_gnss_alarms': qs.count(),
            'active_gnss_alarms': active.count(),
            'by_severity': by_severity,
        })
