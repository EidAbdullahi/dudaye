from django.urls import path
from . import views

app_name = 'clients'  # ✅ Required for namespacing

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('add/', views.add_client, name='add_client'),
]
