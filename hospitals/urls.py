from django.urls import path
from . import views

app_name = "hospitals"

urlpatterns = [
    # Hospital list
    path("", views.hospital_list, name="hospital_list"),

    # Add hospital
    path("add/", views.hospital_form, name="hospital_form"),

    # Edit hospital
    path("edit/<int:pk>/", views.hospital_form, name="edit_hospital"),

    # Hospital detail view
    path("detail/<int:pk>/", views.hospital_detail, name="hospital_detail"),

    # Hospital dashboard (for hospital users)
    path("dashboard/", views.hospital_dashboard, name="dashboard"),

    # Submit claim (for hospital users)
    path("submit-claim/", views.submit_claim, name="submit_claim"),
    path('dashboard/', views.hospital_dashboard, name='dashboard'),

]
