from django.urls import path
from . import views

app_name = "clients"  # important for namespacing

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('add/', views.add_client, name='add_client'),
    path('edit/<int:pk>/', views.edit_client, name='edit_client'),  # 🔹 add this
    path('<int:pk>/', views.client_detail, name='client_detail'),
]
