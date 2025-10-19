from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from django.utils import timezone

from .models import Policy
from .serializers import PolicySerializer
from clients.models import Client
from accounts.utils import roles_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from django.utils import timezone
from django.db import IntegrityError

from .models import Policy
from .serializers import PolicySerializer
from clients.models import Client
from accounts.utils import roles_required
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
    Auto-generates a unique policy_number for new policies.
    """
    policy = None
    if pk:
        policy = get_object_or_404(Policy, pk=pk)

    clients = Client.objects.all()
    policy_types = Policy.POLICY_TYPE

    # Auto-generate a unique policy_number for new policies
    import uuid
    auto_policy_number = f"POL-{uuid.uuid4().hex[:8].upper()}"
    if policy:
        auto_policy_number = policy.policy_number

    if request.method == "POST":
        data = request.POST
        client_id = data.get("client")
        client = get_object_or_404(Client, pk=client_id)

        # Use submitted policy_number or auto-generate for new
        policy_number = data.get("policy_number") or auto_policy_number

        required_fields = ["type", "start_date", "end_date", "premium"]
        if all(data.get(f) for f in required_fields):
            try:
                if policy:
                    # Edit existing policy
                    policy.client = client
                    policy.policy_number = policy_number
                    policy.type = data.get("type")
                    policy.start_date = data.get("start_date")
                    policy.end_date = data.get("end_date")
                    policy.premium = data.get("premium")
                    policy.active = data.get("active") == "on"
                    policy.save()
                    messages.success(request, f"Policy '{policy.policy_number}' updated successfully.")
                else:
                    # Add new policy
                    Policy.objects.create(
                        client=client,
                        policy_number=policy_number,
                        type=data.get("type"),
                        start_date=data.get("start_date"),
                        end_date=data.get("end_date"),
                        premium=data.get("premium"),
                        active=data.get("active") == "on",
                        created_by=request.user,
                    )
                    messages.success(request, f"Policy '{policy_number}' added successfully.")

                return redirect("policies:policy_list")

            except IntegrityError:
                # If the generated policy_number already exists, try again
                messages.error(request, "Policy number conflict. Please try again.")
        else:
            messages.error(request, "Please fill all required fields.")

    context = {
        "policy": policy,
        "clients": clients,
        "policy_types": policy_types,
        "dashboard_title": "Edit Policy" if policy else "Add New Policy",
        "role": request.user.role,
        "auto_policy_number": auto_policy_number,
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


# ==============================
# Helper: Auto-create health policy
# ==============================
def create_health_policy(client, created_by):
    """
    Automatically create a Health Policy for a given client.
    """
    policy_number = f"H-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    start_date = timezone.now().date()
    end_date = start_date.replace(year=start_date.year + 1)
    premium_amount = 500.00  # Default premium

    policy = Policy.objects.create(
        client=client,
        policy_number=policy_number,
        type="health",
        start_date=start_date,
        end_date=end_date,
        premium=premium_amount,
        active=True,
        created_by=created_by,
    )
    return policy