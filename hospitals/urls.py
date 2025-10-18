from django.urls import path
from . import views

app_name = "hospitals"

urlpatterns = [
    path("", views.hospital_list, name="hospital_list"),
    path("add/", views.hospital_form, name="add_hospital"),
    path("edit/<int:pk>/", views.hospital_form, name="edit_hospital"),
    path("<int:pk>/", views.hospital_detail, name="hospital_detail"),
]
