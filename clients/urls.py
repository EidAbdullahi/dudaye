from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ClientViewSet

app_name = "clients"  # important for namespacing

# DRF router for standard CRUD API endpoints
router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')

urlpatterns = [
    # Web views
    path('', views.client_list, name='client_list'),
    path('add/', views.add_client, name='add_client'),
    path('edit/<int:pk>/', views.edit_client, name='edit_client'),
    path('<int:pk>/', views.client_detail, name='client_detail'),

    # API endpoints
    path('api/', include(router.urls)),  # => /api/clients/, /api/clients/<pk>/
    path('api/clients/verify/', ClientViewSet.as_view({'post': 'verify_fingerprint'}), name='verify_fingerprint'),
]
