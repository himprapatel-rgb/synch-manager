"""
War Mode URL routing for Synch-Manager.

DRF router configuration for war mode endpoints.
"""

from rest_framework.routers import DefaultRouter

from .views import (
    WarModeSessionViewSet, WarModeTransitionViewSet,
    TimingSourceFailoverViewSet, HoldoverEventViewSet,
    TacticalDomainViewSet, CSACStatusViewSet,
    TacticalDashboardView,
)

router = DefaultRouter()
router.register(r'sessions', WarModeSessionViewSet, basename='warmode-session')
router.register(r'transitions', WarModeTransitionViewSet, basename='warmode-transition')
router.register(r'failovers', TimingSourceFailoverViewSet, basename='timing-failover')
router.register(r'holdovers', HoldoverEventViewSet, basename='holdover-event')
router.register(r'domains', TacticalDomainViewSet, basename='tactical-domain')
router.register(r'csac', CSACStatusViewSet, basename='csac-status')
router.register(r'dashboard', TacticalDashboardView, basename='tactical-dashboard')

urlpatterns = router.urls
