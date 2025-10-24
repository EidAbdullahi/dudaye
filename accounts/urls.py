from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),  # Admin/Finance
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),

    # Users
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),

    # Agents
    path('agents/register/', views.register_agent, name='register_agent'),
    path('agents/', views.agent_list, name='agent_list'),
]
