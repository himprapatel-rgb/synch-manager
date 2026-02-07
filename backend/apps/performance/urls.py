"""
URL routing for Performance Management app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'metrics', views.PerformanceMetricViewSet, basename='performance-metric')
router.register(r'sync-mesh-score', views.SyncMeshScoreViewSet, basename='sync-mesh-score')
router.register(r'mtie-masks', views.MTIEMaskViewSet, basename='mtie-mask')
router.register(r'thresholds', views.PerformanceThresholdViewSet, basename='performance-threshold')

app_name = 'performance'

urlpatterns = [
    path('', include(router.urls)),
]
