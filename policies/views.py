from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from rest_framework import viewsets, permissions
from django.utils import timezone
import uuid

from .models import Policy
from .serializers import PolicySerializer
from clients.models import Client
from accounts.utils import roles_required

# ==============================
# DRF API View
# ==============================
class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    permission_classes = [permissions.IsAuthenticated]

# ==============================
# Web Views
# ==============================
from django.utils import timezone

@login_required
@roles_required("admin", "finance_officer")
def policy_list(request):
    policies = Policy.objects.all()
    now = timezone.now().date()
    for policy in policies:
        if policy.expiry_date:
            policy.days_left = (policy.expiry_date - now).days
        else:
            policy.days_left = 0
    return render(request, "policies/policy_list.html", {
        "policies": policies,
        "dashboard_title": "Policies",
        "role": getattr(request.user, "role", "guest")
    })


@login_required
@roles_required("admin", "finance_officer")
def policy_form(request, pk=None):
    policy = None
    if pk:
        policy = get_object_or_404(Policy, pk=pk)

    clients = Client.objects.all()
    policy_types = Policy.POLICY_TYPE
    auto_policy_number = policy.policy_number if policy else f"POL-{uuid.uuid4().hex[:8].upper()}"
    today = timezone.now().date()
    next_year = today.replace(year=today.year + 1)

    if request.method == "POST":
        data = request.POST
        client = get_object_or_404(Client, pk=data.get("client"))
        policy_number = data.get("policy_number") or auto_policy_number

        # Required fields
        required_fields = ["policy_type", "start_date", "expiry_date", "premium"]
        if all(data.get(f) for f in required_fields):
            try:
                if policy:
                    # Update existing policy
                    policy.client = client
                    policy.policy_number = policy_number
                    policy.policy_type = data.get("policy_type")
                    policy.start_date = data.get("start_date")
                    policy.expiry_date = data.get("expiry_date")
                    policy.premium = data.get("premium")
                    policy.is_active = data.get("is_active") == "on"
                    policy.coverage_details = data.get("coverage_details", "")
                    policy.max_claim_limit = data.get("max_claim_limit") or 0
                    policy.waiting_period_days = data.get("waiting_period_days") or 0
                    policy.save()
                    messages.success(request, f"Policy '{policy.policy_number}' updated successfully.")
                else:
                    # Create new policy
                    Policy.objects.create(
                        client=client,
                        policy_number=policy_number,
                        policy_type=data.get("policy_type"),
                        start_date=data.get("start_date"),
                        expiry_date=data.get("expiry_date"),
                        premium=data.get("premium"),
                        is_active=data.get("is_active") == "on",
                        coverage_details=data.get("coverage_details", ""),
                        max_claim_limit=data.get("max_claim_limit") or 0,
                        waiting_period_days=data.get("waiting_period_days") or 0,
                        created_by=request.user,
                    )
                    messages.success(request, f"Policy '{policy_number}' added successfully.")
                return redirect("policies:policy_list")
            except IntegrityError:
                messages.error(request, "Policy number conflict. Please try again.")
        else:
            messages.error(request, "Please fill all required fields.")

    return render(request, "policies/policy_form.html", {
        "policy": policy,
        "clients": clients,
        "policy_types": policy_types,
        "dashboard_title": "Edit Policy" if policy else "Add New Policy",
        "role": getattr(request.user, "role", "guest"),
        "auto_policy_number": auto_policy_number,
        "today": today,
        "next_year": next_year,
    })


@login_required
def policy_detail(request, pk):
    policy = get_object_or_404(Policy, pk=pk)
    return render(request, "policies/policy_detail.html", {
        "policy": policy,
        "dashboard_title": f"Policy: {policy.policy_number}",
        "role": getattr(request.user, "role", "guest"),
    })


# ==============================
# Auto-create default health policy
# ==============================
def create_health_policy(client, created_by):
    policy_number = f"H-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    start_date = timezone.now().date()
    expiry_date = start_date.replace(year=start_date.year + 1)
    premium_amount = 500.00

    return Policy.objects.create(
        client=client,
        policy_number=policy_number,
        policy_type="health",
        start_date=start_date,
        expiry_date=expiry_date,
        premium=premium_amount,
        is_active=True,
        created_by=created_by,
    )
