"""URL configuration for Synch-Manager."""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    # JWT auth
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # App endpoints
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/fault/', include('apps.fault.urls')),
    path('api/v1/performance/', include('apps.performance.urls')),
    # Prometheus metrics
    path('', include('django_prometheus.urls')),
    # Health check
    path('api/v1/health/', lambda r: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok'})),
]
