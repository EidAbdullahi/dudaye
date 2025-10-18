from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

# Main views
from accounts.views import dashboard
from clients.views import ClientViewSet
from policies.views import PolicyViewSet
from claims.views import ClaimViewSet
from hospitals.views import HospitalViewSet

# =========================
# 🌐 API Routers
# =========================
router = routers.DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'policies', PolicyViewSet)
router.register(r'claims', ClaimViewSet)
router.register(r'hospitals', HospitalViewSet)

# =========================
# 🌍 URL Patterns
# =========================
urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Authentication & accounts
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),

    # Dashboard (main entry)
    path('dashboard/', dashboard, name='main_dashboard'),

    # Clients
    path('clients/', include(('clients.urls', 'clients'), namespace='clients')),

    # Policies
    path('policies/', include(('policies.urls', 'policies'), namespace='policies')),

    # Claims
    path('claims/', include(('claims.urls', 'claims'), namespace='claims')),

    # Hospitals
    path('hospitals/', include(('hospitals.urls', 'hospitals'), namespace='hospitals')),

    # REST API endpoints
    path('api/', include(router.urls)),
]
