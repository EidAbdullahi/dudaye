from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'hospitals', views.HospitalViewSet)

app_name = 'hospitals'

urlpatterns = [
    path('', views.hospital_list, name='hospital_list'),
    path('dashboard/', views.hospital_dashboard, name='dashboard'),
    path('submit-claim/', views.submit_claim, name='submit_claim'),
    path('add/', views.hospital_form, name='add_hospital'),          # ✅ use hospital_form
    path('<int:pk>/', views.hospital_detail, name='hospital_detail'),
    path('<int:pk>/edit/', views.hospital_form, name='edit_hospital'), # ✅ edit uses same view
    path('api/', include(router.urls)),
]
