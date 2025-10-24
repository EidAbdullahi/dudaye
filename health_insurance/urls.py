from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('hospitals/', include('hospitals.urls', namespace='hospitals')),
    path('claims/', include('claims.urls', namespace='claims')),
    path('clients/', include('clients.urls', namespace='clients')),
    path('policies/', include('policies.urls', namespace='policies')),
]
