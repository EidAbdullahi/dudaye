from django.urls import path
from . import views

app_name = "hospitals"

urlpatterns = [
    path("list/", views.hospital_list, name="hospital_list"),
    path("add/", views.hospital_form, name="hospital_form"),           # For adding new hospital
    path("<int:pk>/edit/", views.hospital_form, name="edit_hospital"), # For editing hospital
    path("<int:pk>/", views.hospital_detail, name="hospital_detail"),  # View hospital
    path("dashboard/", views.hospital_dashboard, name="dashboard"),
]
