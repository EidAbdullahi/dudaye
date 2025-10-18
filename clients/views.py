from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions

from .models import Client
from .serializers import ClientSerializer
from accounts.utils import roles_required

# -----------------------------
# API ViewSet
# -----------------------------
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

# -----------------------------
# Web Views
# -----------------------------
@login_required
@roles_required("admin")
def client_list(request):
    """
    Admin / Superuser: See all clients
    Agent: See only own clients
    """
    user = request.user
    role = getattr(user, "role", "guest")

    if role == "agent":
        clients = Client.objects.filter(agent=user)
    else:
        clients = Client.objects.all()

    context = {
        "clients": clients,
        "role": role,
        "user": user,
        "dashboard_title": "Clients Directory",
    }
    return render(request, "clients/client_list.html", context)


@login_required
@roles_required("admin", "agent")
def add_client(request):
    """
    Admin / Superuser: Can add any client
    Agent: Can add clients assigned to them
    """
    user = request.user
    role = getattr(user, "role", "guest")

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        if first_name and last_name and email:
            Client.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                created_by=user,
                agent=user if role == "agent" else None,
            )
            messages.success(request, f"Client {first_name} {last_name} added successfully.")
            return redirect("clients:client_list")
        else:
            messages.error(request, "Please fill all required fields.")

    context = {
        "dashboard_title": "Add New Client",
        "user": user,
        "role": role,
    }
    return render(request, "clients/add_client.html", context)
