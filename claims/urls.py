from django.urls import path
from . import views

app_name = "claims"

urlpatterns = [
    path("", views.claim_list, name="claim_list"),
    path("add/", views.add_claim, name="add_claim"),  # Only hospital users
    path("edit/<int:pk>/", views.edit_claim, name="edit_claim"),
    path("detail/<int:pk>/", views.claim_detail, name="claim_detail"),
    path("approve/<int:pk>/", views.approve_claim, name="approve_claim"),
    path("reject/<int:pk>/", views.reject_claim, name="reject_claim"),
]
