from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions

from .models import Client
from .forms import ClientForm
from .serializers import ClientSerializer
from accounts.utils import roles_required


# ==========================
# 🌍 Web Views
# ==========================
@login_required
@roles_required("admin", "agent")
def client_list(request):
    """
    Display a list of clients:
    - Admin: All clients
    - Agent: Only their clients
    """
    user = request.user
    if getattr(user, "role", None) == "agent":
        clients = Client.objects.filter(agent=user)
    else:
        clients = Client.objects.all()

    context = {
        "clients": clients,
        "dashboard_title": "Clients List",
    }
    return render(request, "clients/client_list.html", context)


@login_required
@roles_required("admin", "agent")
def add_client(request):
    """
    Add/register a new client with optional fingerprint and photo.
    """
    if request.method == "POST":
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            client = form.save(commit=False)
            fingerprint = request.FILES.get("fingerprint_file")
            if fingerprint:
                client.fingerprint_data = fingerprint.read()
            client.registered_by = request.user
            client.save()
            messages.success(request, f"Client '{client}' registered successfully!")
            return redirect("clients:client_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ClientForm()

    context = {
        "form": form,
        "dashboard_title": "Register New Client",
    }
    return render(request, "clients/client_form.html", context)


@login_required
@roles_required("admin", "agent")
def edit_client(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        form = ClientForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            client = form.save(commit=False)
            fingerprint = request.FILES.get("fingerprint_file")
            if fingerprint:
                client.fingerprint_data = fingerprint.read()
            client.save()
            messages.success(request, f"Client '{client.first_name} {client.last_name}' updated successfully!")
            return redirect("clients:client_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Important: Pass the instance to prefill the form
        form = ClientForm(instance=client)

    return render(request, "clients/client_form.html", {
        "form": form,
        "dashboard_title": f"Edit Client: {client.first_name} {client.last_name}"
    })


@login_required
@roles_required("admin", "agent")
def client_detail(request, pk):
    """
    View details of a single client.
    """
    client = get_object_or_404(Client, pk=pk)
    context = {
        "client": client,
        "dashboard_title": f"Client: {client.first_name} {client.last_name}",
    }
    return render(request, "clients/client_detail.html", context)


# ==========================
# 🌐 API Views (DRF)
# ==========================
class ClientViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage clients.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
