from django.urls import path
from . import views

app_name = 'claims'

urlpatterns = [
    path('', views.claim_list, name='claim_list'),
    path('add/', views.add_claim, name='add_claim'),
]
