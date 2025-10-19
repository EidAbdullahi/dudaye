from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

# Main views
from accounts.views import dashboard

# =========================
# 🌐 API Routers
# =========================
router = routers.DefaultRouter()

# Import ViewSets **inside here** to avoid circular imports
from clients.views import ClientViewSet
from policies.views import PolicyViewSet
from claims.views import ClaimViewSet
from hospitals.views import HospitalViewSet

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

    # Apps
    path('clients/', include(('clients.urls', 'clients'), namespace='clients')),
    path('policies/', include(('policies.urls', 'policies'), namespace='policies')),
    path('claims/', include(('claims.urls', 'claims'), namespace='claims')),
    path('hospitals/', include(('hospitals.urls', 'hospitals'), namespace='hospitals')),

    # REST API
    path('api/', include(router.urls)),
]