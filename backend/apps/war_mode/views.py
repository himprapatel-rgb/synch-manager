"""
War Mode Views for Synch-Manager.

DRF viewsets and custom actions for war mode session management,
tactical timing coordination, holdover monitoring, and CSAC control.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    WarModeSession, WarModeTransition, TimingSourceFailover,
    HoldoverEvent, TacticalDomain, CSACStatus,
    WarModeLevel,
)
from .serializers import (
    WarModeSessionSerializer, WarModeTransitionSerializer,
    TimingSourceFailoverSerializer, HoldoverEventSerializer,
    TacticalDomainSerializer, CSACStatusSerializer,
    WarModeActivateSerializer, TacticalStatusSerializer,
)


class WarModeSessionViewSet(viewsets.ModelViewSet):
    """Manage war mode sessions."""
    queryset = WarModeSession.objects.all()
    serializer_class = WarModeSessionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        is_active = self.request.query_params.get('active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return qs

    @action(detail=False, methods=['post'])
    def activate(self, request):
        """Activate a new war mode session."""
        serializer = WarModeActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Deactivate any currently active sessions
        WarModeSession.objects.filter(is_active=True).update(
            is_active=False, deactivated_at=timezone.now()
        )

        session = WarModeSession.objects.create(
            level=serializer.validated_data['level'],
            threat_type=serializer.validated_data['threat_type'],
            reason=serializer.validated_data.get('reason', ''),
            threat_indicators=serializer.validated_data.get('threat_indicators', {}),
            activated_by=request.user.username if request.user.is_authenticated else 'system',
        )

        return Response(
            WarModeSessionSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a war mode session."""
        session = self.get_object()
        if not session.is_active:
            return Response(
                {'error': 'Session already deactivated'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.is_active = False
        session.deactivated_at = timezone.now()
        session.save()
        return Response(WarModeSessionSerializer(session).data)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the currently active war mode session."""
        session = WarModeSession.objects.filter(is_active=True).first()
        if session:
            return Response(WarModeSessionSerializer(session).data)
        return Response({'status': 'PEACETIME', 'active_session': None})


class WarModeTransitionViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to war mode transitions."""
    queryset = WarModeTransition.objects.all()
    serializer_class = WarModeTransitionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        session_id = self.request.query_params.get('session')
        if session_id:
            qs = qs.filter(session_id=session_id)
        return qs


class TimingSourceFailoverViewSet(viewsets.ModelViewSet):
    """Manage timing source failover events."""
    queryset = TimingSourceFailover.objects.all()
    serializer_class = TimingSourceFailoverSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        ne_id = self.request.query_params.get('network_element')
        if ne_id:
            qs = qs.filter(network_element_id=ne_id)
        hours = self.request.query_params.get('hours')
        if hours:
            cutoff = timezone.now() - timedelta(hours=int(hours))
            qs = qs.filter(switched_at__gte=cutoff)
        return qs

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get failovers from the last 24 hours."""
        cutoff = timezone.now() - timedelta(hours=24)
        failovers = TimingSourceFailover.objects.filter(switched_at__gte=cutoff)
        return Response(TimingSourceFailoverSerializer(failovers, many=True).data)


class HoldoverEventViewSet(viewsets.ModelViewSet):
    """Manage holdover events."""
    queryset = HoldoverEvent.objects.all()
    serializer_class = HoldoverEventSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        active = self.request.query_params.get('active')
        if active is not None:
            qs = qs.filter(is_active=active.lower() == 'true')
        ne_id = self.request.query_params.get('network_element')
        if ne_id:
            qs = qs.filter(network_element_id=ne_id)
        return qs

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End an active holdover event."""
        event = self.get_object()
        if not event.is_active:
            return Response(
                {'error': 'Holdover event already ended'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        event.is_active = False
        event.ended_at = timezone.now()
        event.save()
        return Response(HoldoverEventSerializer(event).data)


class TacticalDomainViewSet(viewsets.ModelViewSet):
    """Manage tactical domains."""
    queryset = TacticalDomain.objects.all()
    serializer_class = TacticalDomainSerializer

    @action(detail=True, methods=['post'])
    def enable_mesh(self, request, pk=None):
        """Enable sync mesh for a tactical domain."""
        domain = self.get_object()
        domain.sync_mesh_enabled = True
        domain.emcon_active = False
        domain.save()
        return Response(TacticalDomainSerializer(domain).data)

    @action(detail=True, methods=['post'])
    def enable_emcon(self, request, pk=None):
        """Enable EMCON (emissions control) for a domain."""
        domain = self.get_object()
        domain.emcon_active = True
        domain.sync_mesh_enabled = False
        domain.save()
        return Response(TacticalDomainSerializer(domain).data)


class CSACStatusViewSet(viewsets.ModelViewSet):
    """Manage CSAC status per network element."""
    queryset = CSACStatus.objects.all()
    serializer_class = CSACStatusSerializer

    @action(detail=True, methods=['post'])
    def activate_csac(self, request, pk=None):
        """Activate CSAC on a network element."""
        csac = self.get_object()
        csac.is_active = True
        csac.activated_at = timezone.now()
        csac.save()
        return Response(CSACStatusSerializer(csac).data)

    @action(detail=True, methods=['post'])
    def deactivate_csac(self, request, pk=None):
        """Deactivate CSAC."""
        csac = self.get_object()
        csac.is_active = False
        csac.is_ready = False
        csac.power_watts = 0.0
        csac.save()
        return Response(CSACStatusSerializer(csac).data)


class TacticalDashboardView(viewsets.ViewSet):
    """Tactical timing dashboard aggregations."""

    def list(self, request):
        """Get tactical timing dashboard summary."""
        now = timezone.now()
        last_24h = now - timedelta(hours=24)

        data = {
            'active_sessions': WarModeSession.objects.filter(is_active=True).count(),
            'total_domains': TacticalDomain.objects.count(),
            'domains_in_war_mode': TacticalDomain.objects.exclude(
                current_level=WarModeLevel.PEACETIME
            ).count(),
            'active_holdovers': HoldoverEvent.objects.filter(is_active=True).count(),
            'recent_failovers': TimingSourceFailover.objects.filter(
                switched_at__gte=last_24h
            ).count(),
            'sync_mesh_domains': TacticalDomain.objects.filter(
                sync_mesh_enabled=True
            ).count(),
            'emcon_domains': TacticalDomain.objects.filter(
                emcon_active=True
            ).count(),
        }

        serializer = TacticalStatusSerializer(data)
        return Response(serializer.data)
