from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from .models import Policy
from .serializers import PolicySerializer
from clients.models import Client
from accounts.utils import roles_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.utils import roles_required
from .models import Policy
from clients.models import Client

@login_required
@roles_required("admin", "finance_officer")
def policy_form(request, pk=None):
    """
    Add or Edit Policy
    - pk=None → Add new policy
    - pk provided → Edit existing policy
    """
    policy = None
    if pk:
        policy = get_object_or_404(Policy, pk=pk)

    clients = Client.objects.all()
    policy_types = Policy.POLICY_TYPE

    if request.method == "POST":
        data = request.POST
        client_id = data.get("client")
        client = get_object_or_404(Client, pk=client_id)

        policy_number = data.get("policy_number")
        policy_type = data.get("type")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        premium = data.get("premium")
        active = data.get("active") == "on"

        if all([client, policy_number, policy_type, start_date, end_date, premium]):
            if policy:
                # Edit existing policy
                policy.client = client
                policy.policy_number = policy_number
                policy.type = policy_type
                policy.start_date = start_date
                policy.end_date = end_date
                policy.premium = premium
                policy.active = active
                policy.save()
                messages.success(request, f"Policy '{policy.policy_number}' updated successfully.")
            else:
                # Add new policy
                Policy.objects.create(
                    client=client,
                    policy_number=policy_number,
                    type=policy_type,
                    start_date=start_date,
                    end_date=end_date,
                    premium=premium,
                    active=active,
                    created_by=request.user,
                )
                messages.success(request, f"Policy '{policy_number}' added successfully.")

            return redirect("policies:policy_list")
        else:
            messages.error(request, "Please fill all required fields.")

    context = {
        "policy": policy,
        "clients": clients,
        "policy_types": policy_types,
        "dashboard_title": "Edit Policy" if policy else "Add New Policy",
        "role": request.user.role,
    }
    return render(request, "policies/policy_form.html", context)

# ==============================
# 🌐 API ViewSet (DRF)
# ==============================
class PolicyViewSet(viewsets.ModelViewSet):
    """
    REST API endpoint for policies.
    Only authenticated users can access.
    """
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    permission_classes = [permissions.IsAuthenticated]

# ==============================
# 🌍 Web Views
# ==============================

@login_required
@roles_required("admin", "finance_officer")
def policy_list(request):
    """
    Show all policies for admin/finance or active only for others.
    """
    user = request.user
    role = getattr(user, "role", "guest")
    if user.is_superuser or role in ["admin", "finance_officer"]:
        policies = Policy.objects.all()
    else:
        policies = Policy.objects.filter(active=True)

    context = {
        "policies": policies,
        "role": role,
        "dashboard_title": "Policies",
    }
    return render(request, "policies/policy_list.html", context)


@login_required
@roles_required("admin", "finance_officer")
def policy_form(request, pk=None):
    """
    Handles Add or Edit Policy.
    pk=None -> Add, pk provided -> Edit
    """
    policy = None
    if pk:
        policy = get_object_or_404(Policy, pk=pk)

    if request.method == "POST":
        data = request.POST
        client_id = data.get("client")
        client = get_object_or_404(Client, pk=client_id)

        required_fields = ["policy_number", "type", "start_date", "end_date", "premium"]
        if all(data.get(f) for f in required_fields):
            if policy:
                # Edit
                policy.client = client
                policy.policy_number = data.get("policy_number")
                policy.type = data.get("type")
                policy.start_date = data.get("start_date")
                policy.end_date = data.get("end_date")
                policy.premium = data.get("premium")
                policy.active = data.get("active") == "on"
                policy.save()
                messages.success(request, f"Policy '{policy.policy_number}' updated successfully.")
            else:
                # Add
                Policy.objects.create(
                    client=client,
                    policy_number=data.get("policy_number"),
                    type=data.get("type"),
                    start_date=data.get("start_date"),
                    end_date=data.get("end_date"),
                    premium=data.get("premium"),
                    active=data.get("active") == "on",
                    created_by=request.user,
                )
                messages.success(request, f"Policy '{data.get('policy_number')}' added successfully.")

            return redirect("policies:policy_list")
        else:
            messages.error(request, "Please fill all required fields.")

    clients = Client.objects.all()
    context = {
        "policy": policy,
        "clients": clients,
        "dashboard_title": "Edit Policy" if policy else "Add New Policy",
        "role": request.user.role,
    }
    return render(request, "policies/policy_form.html", context)


@login_required
def policy_detail(request, pk):
    """
    View detailed policy information (read-only).
    """
    policy = get_object_or_404(Policy, pk=pk)

    context = {
        "policy": policy,
        "dashboard_title": f"Policy: {policy.policy_number}",
        "role": getattr(request.user, "role", "guest"),
    }
    return render(request, "policies/policy_detail.html", context)
