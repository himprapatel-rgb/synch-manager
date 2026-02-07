"""NTG App URL Routing - National Timing Grid API endpoints"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    NTGNodeViewSet, AtomicClockViewSet, CVTTViewSet,
    JammingEventViewSet, SpoofingEventViewSet,
    ClockStabilityViewSet, AntennaEnvironmentViewSet,
    PTPLinkEvaluationViewSet, TimingGridStatusViewSet,
)

router = DefaultRouter()
router.register(r'nodes', NTGNodeViewSet, basename='ntg-node')
router.register(r'atomic-clocks', AtomicClockViewSet, basename='atomic-clock')
router.register(r'cvtt', CVTTViewSet, basename='cvtt')
router.register(r'jamming-events', JammingEventViewSet, basename='jamming-event')
router.register(r'spoofing-events', SpoofingEventViewSet, basename='spoofing-event')
router.register(r'clock-stability', ClockStabilityViewSet, basename='clock-stability')
router.register(r'antenna-environment', AntennaEnvironmentViewSet, basename='antenna-environment')
router.register(r'ptp-link-evaluation', PTPLinkEvaluationViewSet, basename='ptp-link-evaluation')
router.register(r'grid-status', TimingGridStatusViewSet, basename='grid-status')

urlpatterns = [
    path('', include(router.urls)),
]
