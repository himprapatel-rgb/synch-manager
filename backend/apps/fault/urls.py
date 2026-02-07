from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AlarmViewSet, EventViewSet, AlarmPolicyViewSet,
    GNSSAlarmSummaryViewSet,
)

router = DefaultRouter()
router.register(r'alarms', AlarmViewSet, basename='alarm')
router.register(r'events', EventViewSet, basename='event')
router.register(r'alarm-policies', AlarmPolicyViewSet, basename='alarm-policy')
router.register(r'gnss-summary', GNSSAlarmSummaryViewSet, basename='gnss-alarm-summary')

urlpatterns = [
    path('', include(router.urls)),
]
