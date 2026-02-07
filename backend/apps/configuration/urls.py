from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ConfigurationPolicyViewSet, ComplianceAuditViewSet,
    FirmwarePolicyViewSet, ConfigurationSnapshotViewSet,
    TimingSourcePriorityViewSet,
)

router = DefaultRouter()
router.register(r'sync-policies', ConfigurationPolicyViewSet, basename='sync-policy')
router.register(r'compliance-audits', ComplianceAuditViewSet, basename='compliance-audit')
router.register(r'firmware', FirmwarePolicyViewSet, basename='firmware')
router.register(r'config-snapshots', ConfigurationSnapshotViewSet, basename='config-snapshot')
router.register(r'zero-trust-sources', TimingSourcePriorityViewSet, basename='zero-trust-source')

urlpatterns = [
    path('', include(router.urls)),
]
