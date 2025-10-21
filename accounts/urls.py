from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("users/", views.user_list, name="user_list"),
    path("users/<int:user_id>/toggle/", views.toggle_user_status, name="toggle_user_status"),
]
