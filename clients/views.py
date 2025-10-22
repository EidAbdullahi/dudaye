from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from rest_framework import viewsets, permissions

from .models import Client
from .forms import ClientForm
from .serializers import ClientSerializer
from accounts.utils import roles_required
from accounts.models import User  # assuming your Agent is a User with role='agent'


# ==========================
# 🌍 Web Views
# ==========================
@login_required
@roles_required("admin", "agent")
def client_list(request):
    """
    Display a list of clients with search and filter:
    - Admin: All clients
    - Agent: Only their clients
    - Supports search (by name, email, phone)
    - Filter by gender and agent (admin only)
    - Includes pagination
    """
    user = request.user
    search_query = request.GET.get("search", "").strip()
    gender_filter = request.GET.get("gender", "").strip()
    agent_filter = request.GET.get("agent", "").strip()

    # Base queryset
    if getattr(user, "role", None) == "agent":
        clients = Client.objects.filter(agent=user)
    else:
        clients = Client.objects.all()

    # 🔍 Search
    if search_query:
        clients = clients.filter(
            first_name__icontains=search_query
        ) | clients.filter(
            last_name__icontains=search_query
        ) | clients.filter(
            email__icontains=search_query
        ) | clients.filter(
            phone__icontains=search_query
        )

    # ⚧ Filter by gender
    if gender_filter:
        clients = clients.filter(gender__iexact=gender_filter)

    # 🧑‍💼 Filter by agent (admins only)
    if agent_filter and getattr(user, "role", None) == "admin":
        clients = clients.filter(agent_id=agent_filter)

    # 📑 Pagination (10 per page)
    paginator = Paginator(clients.order_by("-created_at"), 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Agents list for admin filter dropdown
    agents = None
    if getattr(user, "role", None) == "admin":
        agents = User.objects.filter(role="agent")

    context = {
        "clients": page_obj,  # paginated
        "page_obj": page_obj,
        "agents": agents,
        "search_query": search_query,
        "gender_filter": gender_filter,
        "agent_filter": agent_filter,
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
