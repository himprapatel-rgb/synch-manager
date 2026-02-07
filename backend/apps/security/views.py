"""
Security & GNSS Resilience Views for Synch-Manager.
"""

from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers as drf_serializers
from django_filters.rest_framework import DjangoFilterBackend

from .models import GNSSStatus, ThreatEvent, WarModeState, AuditLogEntry


# --- Serializers (inline for this app) ---

class GNSSStatusSerializer(drf_serializers.ModelSerializer):
    time_source_display = drf_serializers.CharField(
        source='get_time_source_display', read_only=True,
    )
    class Meta:
        model = GNSSStatus
        fields = '__all__'


class ThreatEventSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = ThreatEvent
        fields = '__all__'


class WarModeStateSerializer(drf_serializers.ModelSerializer):
    state_display = drf_serializers.CharField(
        source='get_current_state_display', read_only=True,
    )
    class Meta:
        model = WarModeState
        fields = '__all__'


class AuditLogSerializer(drf_serializers.ModelSerializer):
    event_type_display = drf_serializers.CharField(
        source='get_event_type_display', read_only=True,
    )
    class Meta:
        model = AuditLogEntry
        fields = '__all__'


# --- ViewSets ---

class GNSSStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """GNSS receiver status per network element."""
    queryset = GNSSStatus.objects.select_related('network_element')
    serializer_class = GNSSStatusSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """Network-wide GNSS health summary."""
        total = GNSSStatus.objects.count()
        locked = GNSSStatus.objects.filter(gnss_locked=True).count()
        spoofing = GNSSStatus.objects.filter(spoofing_detected=True).count()
        jamming = GNSSStatus.objects.filter(jamming_detected=True).count()
        return Response({
            'total_receivers': total,
            'gnss_locked': locked,
            'gnss_unlocked': total - locked,
            'spoofing_detected': spoofing,
            'jamming_detected': jamming,
        })


class ThreatEventViewSet(viewsets.ModelViewSet):
    """GNSS threat events (spoofing, jamming, anomalies)."""
    queryset = ThreatEvent.objects.select_related('network_element')
    serializer_class = ThreatEventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['threat_type', 'severity', 'resolved']

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        """Mark a threat event as resolved."""
        event = self.get_object()
        event.resolved = True
        event.resolved_at = timezone.now()
        event.save()
        return Response(ThreatEventSerializer(event).data)


class WarModeViewSet(viewsets.ViewSet):
    """War Mode state management."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request):
        """Get current War Mode state."""
        state = WarModeState.objects.first()
        if not state:
            state = WarModeState.objects.create()
        return Response(WarModeStateSerializer(state).data)

    @action(detail=False, methods=['post'], url_path='activate')
    def activate(self, request):
        """Activate War Mode."""
        reason = request.data.get('reason', 'Manual activation')
        state, _ = WarModeState.objects.get_or_create(defaults={})
        state.current_state = WarModeState.State.WAR_MODE
        state.activated_at = timezone.now()
        state.activated_by = request.user.username
        state.reason = reason
        state.save()
        return Response(WarModeStateSerializer(state).data)

    @action(detail=False, methods=['post'], url_path='deactivate')
    def deactivate(self, request):
        """Deactivate War Mode (return to normal)."""
        state = WarModeState.objects.first()
        if state:
            state.current_state = WarModeState.State.RECOVERY
            state.save()
        return Response(WarModeStateSerializer(state).data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Tamper-evident audit log."""
    queryset = AuditLogEntry.objects.select_related('network_element')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event_type']
