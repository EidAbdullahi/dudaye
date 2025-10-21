from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from accounts.views import dashboard  # main dashboard

# =========================
# 🌐 API Routers
# =========================
router = routers.DefaultRouter()

# Import ViewSets safely to avoid circular imports
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
    # 🧭 Django Admin
    path('admin/', admin.site.urls),

    # 🔐 User Accounts (Login, Register, Logout)
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),

    # 🧮 Main Dashboard (for Admin / Claim Officer / Finance)
    path('dashboard/', dashboard, name='main_dashboard'),

    # 🏥 Hospital App (Dashboard, Management, etc.)
    path('hospitals/', include(('hospitals.urls', 'hospitals'), namespace='hospitals')),

    # 💰 Claims App (Includes hospital dashboard + claim management)
    path('claims/', include(('claims.urls', 'claims'), namespace='claims')),

    # 👥 Clients App
    path('clients/', include(('clients.urls', 'clients'), namespace='clients')),

    # 📑 Policies App
    path('policies/', include(('policies.urls', 'policies'), namespace='policies')),

    # 🌐 REST API Endpoints
    path('api/', include(router.urls)),

    # 🔑 API Authentication (DRF Browsable API login)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# =========================
# ⚙️ Optional: Static/Media (if using local file uploads)
# =========================
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
