from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'policies'  # For namespacing in templates

# DRF router for API
router = routers.DefaultRouter()
router.register(r'policies', views.PolicyViewSet, basename='policy')

urlpatterns = [
    # Web views
    path('', views.policy_list, name='policy_list'),               # List all policies
    path('add/', views.policy_form, name='add_policy'),            # Add new policy
    path('<int:pk>/edit/', views.policy_form, name='edit_policy'), # Edit existing policy
    path('<int:pk>/', views.policy_detail, name='policy_detail'),  # View policy details

    # API endpoints
    path('api/', include(router.urls)),
]