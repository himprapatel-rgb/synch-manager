"""NTG (National Timing Grid) App Views - DRF ViewSets

Provides API endpoints for:
- NTG nodes management
- Atomic clock monitoring
- Common View Time Transfer measurements
- Jamming/Spoofing event detection
- Clock stability tracking
- Antenna environment monitoring
- PTP link evaluation
- Grid status dashboard
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from datetime import timedelta

from .models import (
    NTGNode, AtomicClock, CommonViewTimeTransfer,
    JammingEvent, SpoofingEvent, ClockStabilityTracking,
    AntennaEnvironment, PTPLinkEvaluation, TimingGridStatus
)
from .serializers import (
    NTGNodeSerializer, AtomicClockSerializer, CVTTSerializer,
    JammingEventSerializer, SpoofingEventSerializer,
    ClockStabilitySerializer, AntennaEnvironmentSerializer,
    PTPLinkEvaluationSerializer, TimingGridStatusSerializer
)


class NTGNodeViewSet(viewsets.ModelViewSet):
    """NTG measurement node management"""
    queryset = NTGNode.objects.all()
    serializer_class = NTGNodeSerializer
    filterset_fields = ['status', 'gps_enabled', 'galileo_enabled', 'jamming_detection_enabled']
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'installed_at', 'last_seen']
    
    @action(detail=True, methods=['post'])
    def enable_all_gnss(self, request, pk=None):
        """Enable all GNSS constellations on a node"""
        node = self.get_object()
        node.gps_enabled = True
        node.galileo_enabled = True
        node.glonass_enabled = True
        node.beidou_enabled = True
        node.save()
        return Response({'status': 'All GNSS constellations enabled'})
    
    @action(detail=True, methods=['post'])
    def enable_security_features(self, request, pk=None):
        """Enable all security features (jamming, spoofing, spectrum monitoring)"""
        node = self.get_object()
        node.jamming_detection_enabled = True
        node.spoofing_detection_enabled = True
        node.spectrum_monitoring_enabled = True
        node.save()
        return Response({'status': 'Security features enabled'})
    
    @action(detail=True, methods=['get'])
    def health_status(self, request, pk=None):
        """Get comprehensive health status for a node"""
        node = self.get_object()
        recent_env = AntennaEnvironment.objects.filter(
            node=node
        ).order_by('-timestamp').first()
        
        active_jamming = JammingEvent.objects.filter(node=node, is_active=True).count()
        active_spoofing = SpoofingEvent.objects.filter(node=node, is_active=True).count()
        
        return Response({
            'node_id': str(node.id),
            'status': node.status,
            'satellites_visible': recent_env.total_satellites_visible if recent_env else None,
            'active_jamming_events': active_jamming,
            'active_spoofing_events': active_spoofing,
            'security_enabled': all([
                node.jamming_detection_enabled,
                node.spoofing_detection_enabled,
                node.spectrum_monitoring_enabled
            ])
        })


class AtomicClockViewSet(viewsets.ModelViewSet):
    """Atomic clock management and monitoring"""
    queryset = AtomicClock.objects.all()
    serializer_class = AtomicClockSerializer
    filterset_fields = ['clock_type', 'status', 'utc_traceable', 'organization']
    search_fields = ['name', 'serial_number', 'organization']
    
    @action(detail=True, methods=['get'])
    def stability_history(self, request, pk=None):
        """Get stability tracking history for an atomic clock"""
        clock = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        records = ClockStabilityTracking.objects.filter(
            atomic_clock=clock,
            timestamp__gte=since
        ).order_by('-timestamp')
        
        return Response(ClockStabilitySerializer(records, many=True).data)
    
    @action(detail=True, methods=['get'])
    def utc_offset_trend(self, request, pk=None):
        """Get UTC offset trend data"""
        clock = self.get_object()
        records = ClockStabilityTracking.objects.filter(
            atomic_clock=clock
        ).order_by('-timestamp')[:100]
        
        return Response({
            'clock_id': str(clock.id),
            'offsets': [
                {'timestamp': r.timestamp, 'offset_ns': r.utc_offset_ns}
                for r in records
            ]
        })
    
    @action(detail=True, methods=['post'])
    def enter_holdover(self, request, pk=None):
        """Manually put clock into holdover mode"""
        clock = self.get_object()
        clock.status = 'holdover'
        clock.save()
        return Response({'status': 'Clock entered holdover mode'})


class CVTTViewSet(viewsets.ModelViewSet):
    """Common View Time Transfer measurements"""
    queryset = CommonViewTimeTransfer.objects.all()
    serializer_class = CVTTSerializer
    filterset_fields = ['gnss_constellation', 'is_valid']
    ordering_fields = ['timestamp', 'time_difference_ns']
    
    @action(detail=False, methods=['get'])
    def compare_nodes(self, request):
        """Compare time difference between two specific nodes"""
        node_a = request.query_params.get('node_a')
        node_b = request.query_params.get('node_b')
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        measurements = CommonViewTimeTransfer.objects.filter(
            node_a_id=node_a,
            node_b_id=node_b,
            timestamp__gte=since,
            is_valid=True
        ).order_by('-timestamp')
        
        return Response(CVTTSerializer(measurements, many=True).data)
    
    @action(detail=False, methods=['get'])
    def accuracy_stats(self, request):
        """Get accuracy statistics for CVTT measurements"""
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        stats = CommonViewTimeTransfer.objects.filter(
            timestamp__gte=since,
            is_valid=True
        ).aggregate(
            avg_difference=Avg('time_difference_ns'),
            max_difference=Max('time_difference_ns'),
            min_difference=Min('time_difference_ns'),
            avg_uncertainty=Avg('uncertainty_ns'),
            count=Count('id')
        )
        
        return Response(stats)


class JammingEventViewSet(viewsets.ModelViewSet):
    """GNSS jamming event detection and tracking"""
    queryset = JammingEvent.objects.all()
    serializer_class = JammingEventSerializer
    filterset_fields = ['severity', 'is_active', 'node']
    ordering_fields = ['detected_at', 'severity']
    
    @action(detail=False, methods=['get'])
    def active_events(self, request):
        """Get all currently active jamming events"""
        events = JammingEvent.objects.filter(is_active=True)
        return Response(JammingEventSerializer(events, many=True).data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark jamming event as resolved"""
        event = self.get_object()
        event.is_active = False
        event.ended_at = timezone.now()
        event.save()
        return Response({'status': 'Jamming event resolved'})


class SpoofingEventViewSet(viewsets.ModelViewSet):
    """GNSS spoofing event detection and tracking"""
    queryset = SpoofingEvent.objects.all()
    serializer_class = SpoofingEventSerializer
    filterset_fields = ['detection_method', 'is_active', 'node']
    ordering_fields = ['detected_at', 'confidence_score']
    
    @action(detail=False, methods=['get'])
    def active_events(self, request):
        """Get all currently active spoofing events"""
        events = SpoofingEvent.objects.filter(is_active=True)
        return Response(SpoofingEventSerializer(events, many=True).data)
    
    @action(detail=False, methods=['get'])
    def by_detection_method(self, request):
        """Get spoofing events grouped by detection method"""
        stats = SpoofingEvent.objects.values('detection_method').annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence_score')
        )
        return Response(list(stats))


class ClockStabilityViewSet(viewsets.ModelViewSet):
    """Clock stability tracking and early warning"""
    queryset = ClockStabilityTracking.objects.all()
    serializer_class = ClockStabilitySerializer
    filterset_fields = ['atomic_clock', 'is_within_spec', 'degradation_detected']
    ordering_fields = ['timestamp']


class AntennaEnvironmentViewSet(viewsets.ModelViewSet):
    """Antenna environment monitoring"""
    queryset = AntennaEnvironment.objects.all()
    serializer_class = AntennaEnvironmentSerializer
    filterset_fields = ['node', 'obstruction_detected', 'interference_detected']
    ordering_fields = ['timestamp']
    
    @action(detail=False, methods=['get'])
    def signal_quality_report(self, request):
        """Get signal quality report for all nodes"""
        latest_per_node = {}
        for env in AntennaEnvironment.objects.order_by('node', '-timestamp').distinct('node'):
            latest_per_node[str(env.node_id)] = {
                'gps_cn0': env.gps_avg_cn0,
                'satellites_visible': env.total_satellites_visible,
                'pdop': env.pdop,
                'obstruction': env.obstruction_detected,
                'interference': env.interference_detected
            }
        return Response(latest_per_node)


class PTPLinkEvaluationViewSet(viewsets.ModelViewSet):
    """PTP link stability evaluation using CVTT"""
    queryset = PTPLinkEvaluation.objects.all()
    serializer_class = PTPLinkEvaluationSerializer
    filterset_fields = ['link_status', 'cvtt_verified', 'meets_itu_g8275_1']
    ordering_fields = ['timestamp', 'path_delay_ns']
    
    @action(detail=False, methods=['get'])
    def compliance_summary(self, request):
        """Get ITU compliance summary for all PTP links"""
        total = PTPLinkEvaluation.objects.count()
        g8275_1 = PTPLinkEvaluation.objects.filter(meets_itu_g8275_1=True).count()
        g8275_2 = PTPLinkEvaluation.objects.filter(meets_itu_g8275_2=True).count()
        
        return Response({
            'total_links': total,
            'g8275_1_compliant': g8275_1,
            'g8275_2_compliant': g8275_2,
            'compliance_rate_g8275_1': (g8275_1 / total * 100) if total > 0 else 0,
            'compliance_rate_g8275_2': (g8275_2 / total * 100) if total > 0 else 0
        })


class TimingGridStatusViewSet(viewsets.ModelViewSet):
    """National Timing Grid status dashboard"""
    queryset = TimingGridStatus.objects.all()
    serializer_class = TimingGridStatusSerializer
    ordering_fields = ['timestamp', 'resilience_score']
    
    @action(detail=False, methods=['get'])
    def current_status(self, request):
        """Get current grid status with live calculations"""
        nodes = NTGNode.objects.all()
        clocks = AtomicClock.objects.all()
        
        return Response({
            'timestamp': timezone.now(),
            'nodes': {
                'total': nodes.count(),
                'online': nodes.filter(status='online').count(),
                'degraded': nodes.filter(status='degraded').count(),
                'offline': nodes.filter(status='offline').count(),
            },
            'atomic_clocks': {
                'total': clocks.count(),
                'operational': clocks.filter(status='operational').count(),
                'holdover': clocks.filter(status='holdover').count(),
                'utc_traceable': clocks.filter(utc_traceable=True).count(),
            },
            'active_threats': {
                'jamming': JammingEvent.objects.filter(is_active=True).count(),
                'spoofing': SpoofingEvent.objects.filter(is_active=True).count(),
            },
            'utc_status': {
                'all_traceable': clocks.filter(utc_traceable=True).count() == clocks.count(),
                'avg_offset_ns': clocks.aggregate(avg=Avg('utc_offset_ns'))['avg'] or 0,
            }
        })
    
    @action(detail=False, methods=['get'])
    def resilience_report(self, request):
        """Generate comprehensive resilience report"""
        nodes = NTGNode.objects.all()
        clocks = AtomicClock.objects.all()
        
        # Calculate resilience factors
        node_availability = (nodes.filter(status='online').count() / nodes.count() * 100) if nodes.count() > 0 else 0
        clock_availability = (clocks.filter(status='operational').count() / clocks.count() * 100) if clocks.count() > 0 else 0
        gnss_diversity = nodes.filter(galileo_enabled=True, gps_enabled=True).count() / nodes.count() * 100 if nodes.count() > 0 else 0
        security_coverage = nodes.filter(jamming_detection_enabled=True, spoofing_detection_enabled=True).count() / nodes.count() * 100 if nodes.count() > 0 else 0
        
        overall_score = (node_availability + clock_availability + gnss_diversity + security_coverage) / 4
        
        return Response({
            'resilience_score': overall_score,
            'factors': {
                'node_availability': node_availability,
                'clock_availability': clock_availability,
                'gnss_diversity': gnss_diversity,
                'security_coverage': security_coverage,
            },
            'recommendations': self._get_recommendations(node_availability, clock_availability, gnss_diversity, security_coverage)
        })
    
    def _get_recommendations(self, node_avail, clock_avail, gnss_div, security):
        recommendations = []
        if node_avail < 90:
            recommendations.append('Increase NTG node redundancy')
        if clock_avail < 90:
            recommendations.append('Review atomic clock maintenance schedule')
        if gnss_div < 80:
            recommendations.append('Enable multi-GNSS on more nodes')
        if security < 90:
            recommendations.append('Enable security features on all nodes')
        return recommendations
