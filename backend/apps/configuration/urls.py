from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SyncPolicyViewSet, ComplianceAuditViewSet,
    FirmwareViewSet, ConfigSnapshotViewSet,
    ZeroTrustTimingSourceViewSet,
)

router = DefaultRouter()
router.register(r'sync-policies', SyncPolicyViewSet, basename='sync-policy')
router.register(r'compliance-audits', ComplianceAuditViewSet, basename='compliance-audit')
router.register(r'firmware', FirmwareViewSet, basename='firmware')
router.register(r'config-snapshots', ConfigSnapshotViewSet, basename='config-snapshot')
router.register(r'zero-trust-sources', ZeroTrustTimingSourceViewSet, basename='zero-trust-source')

urlpatterns = [
    path('', include(router.urls)),
]
