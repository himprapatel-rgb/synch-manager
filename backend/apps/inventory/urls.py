"""
Synch-Manager Inventory URL Configuration

DRF router registration for inventory ViewSets.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(
    r'network-elements', views.NetworkElementViewSet,
    basename='network-element'
)
router.register(
    r'ne-groups', views.NetworkElementGroupViewSet,
    basename='ne-group'
)
router.register(r'cards', views.CardViewSet, basename='card')
router.register(r'ports', views.PortViewSet, basename='port')
router.register(
    r'timing-links', views.TimingLinkViewSet,
    basename='timing-link'
)

app_name = 'inventory'
urlpatterns = [
    path('', include(router.urls)),
]
