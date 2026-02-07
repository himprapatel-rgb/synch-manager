"""PTP App URL Routing - IEEE 1588 PTP Management endpoints"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PTPDomainViewSet, PTPGrandmasterViewSet, PTPClientViewSet,
    PTPMetricsViewSet, PTPTopologyViewSet, LinuxPTPConfigViewSet,
)

router = DefaultRouter()
router.register(r'domains', PTPDomainViewSet, basename='ptp-domain')
router.register(r'grandmasters', PTPGrandmasterViewSet, basename='ptp-grandmaster')
router.register(r'clients', PTPClientViewSet, basename='ptp-client')
router.register(r'metrics', PTPMetricsViewSet, basename='ptp-metrics')
router.register(r'topology', PTPTopologyViewSet, basename='ptp-topology')
router.register(r'linuxptp-config', LinuxPTPConfigViewSet, basename='linuxptp-config')

urlpatterns = [
    path('', include(router.urls)),
]
