"""
Synch-Manager Security URL Configuration

DRF router registration for security ViewSets.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(
    r'gnss-status', views.GNSSStatusViewSet,
    basename='gnss-status'
)
router.register(
    r'threat-events', views.ThreatEventViewSet,
    basename='threat-event'
)
router.register(
    r'war-mode', views.WarModeViewSet,
    basename='war-mode'
)
router.register(
    r'audit-log', views.AuditLogViewSet,
    basename='audit-log'
)

app_name = 'security'
urlpatterns = [
    path('', include(router.urls)),
]
