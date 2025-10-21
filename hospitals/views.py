from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import Sum, F, FloatField
from django.db.models.functions import Coalesce
from rest_framework import viewsets, permissions
import json

# Import models
from .models import Hospital
from .serializers import HospitalSerializer
from clients.models import Client
from policies.models import Policy
from claims.models import Claim
from accounts.utils import roles_required
from .forms import HospitalForm

User = get_user_model()

# =====================================
# 🌐 API ViewSet
# =====================================
class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all().order_by('-created_at')
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated]


# =====================================
# 🏥 HOSPITAL MANAGEMENT VIEWS
# =====================================

@login_required
def hospital_list(request):
    """
    Display hospitals depending on user role.
    - Admin / Finance Officer / Superuser: all hospitals
    - Others: verified only
    """
    user = request.user
    role = getattr(user, "role", "guest")

    if user.is_superuser or role in ["admin", "finance_officer"]:
        hospitals = Hospital.objects.all().order_by('-created_at')
        title = "All Hospitals"
    else:
        hospitals = Hospital.objects.filter(verified=True).order_by('-created_at')
        title = "Verified Hospitals"

    context = {
        "hospitals": hospitals,
        "role": role,
        "user": user,
        "dashboard_title": title,
    }
    return render(request, "hospitals/hospital_list.html", context)


@login_required
def hospital_detail(request, pk):
    """
    Shows full hospital information (read-only).
    """
    hospital = get_object_or_404(Hospital, pk=pk)
    context = {
        "hospital": hospital,
        "role": getattr(request.user, "role", "guest"),
        "dashboard_title": f"Hospital: {hospital.name}",
    }
    return render(request, "hospitals/hospital_detail.html", context)


@login_required
@roles_required("admin", "finance_officer")
def hospital_form(request, pk=None):
    """
    Add or edit a hospital.
    Automatically creates a linked user for new hospitals.
    """
    hospital = None
    if pk:
        hospital = get_object_or_404(Hospital, pk=pk)

    if request.method == "POST":
        form = HospitalForm(request.POST, request.FILES, instance=hospital)
        if form.is_valid():
            hospital_obj = form.save(commit=False)

            if not hospital:
                # Create user for hospital
                username = request.POST.get("username")
                password = request.POST.get("password")
                if not username or not password:
                    messages.error(request, "Username and password are required.")
                    return render(request, "hospitals/hospital_form.html", {"form": form})

                if User.objects.filter(username=username).exists():
                    messages.error(request, f"Username '{username}' is already taken.")
                    return render(request, "hospitals/hospital_form.html", {"form": form})

                user = User.objects.create(
                    username=username,
                    email=form.cleaned_data.get("email"),
                    password=make_password(password),
                    role="hospital",
                    is_active=True
                )
                hospital_obj.user = user
                messages.success(request, f"Hospital '{hospital_obj.name}' created with user '{username}'.")
            else:
                messages.success(request, f"Hospital '{hospital_obj.name}' updated successfully.")

            hospital_obj.save()
            return redirect("hospitals:hospital_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = HospitalForm(instance=hospital)

    context = {
        "form": form,
        "hospital": hospital,
        "dashboard_title": "Edit Hospital" if hospital else "Add New Hospital",
    }
    return render(request, "hospitals/hospital_form.html", context)


# =====================================
# 🏥 HOSPITAL DASHBOARD
# =====================================
@login_required
def hospital_dashboard(request):
    """
    Hospital dashboard with stats, revenue, and pending claims.
    """
    user = request.user
    hospital = getattr(user, "hospital_profile", None)

    if not hospital:
        messages.error(request, "Your hospital profile is missing. Contact admin.")
        return redirect("accounts:dashboard")

    # Claims for this hospital
    claims = Claim.objects.filter(hospital=hospital).order_by("-created_at")

    # Stats
    total_claims = claims.count()
    pending_claims = claims.filter(status="pending").count()
    approved_claims = claims.filter(status="approved").count()
    rejected_claims = claims.filter(status="rejected").count()

    # Revenue collected
    revenue_collected = claims.filter(status__in=["approved", "reimbursed"]).aggregate(
        total=Coalesce(Sum(F("amount"), output_field=FloatField()), 0.0)
    )["total"]

    # Pending claim amount
    pending_amount = claims.filter(status="pending").aggregate(
        total=Coalesce(Sum(F("amount"), output_field=FloatField()), 0.0)
    )["total"]

    context = {
        "dashboard_title": f"{hospital.name} Dashboard",
        "user": user,
        "hospital": hospital,
        "claims": claims,
        "total_claims": total_claims,
        "pending_claims": pending_claims,
        "approved_claims": approved_claims,
        "rejected_claims": rejected_claims,
        "revenue_collected": revenue_collected,
        "pending_amount": pending_amount,
        "recent_claims": claims[:5],
    }

    return render(request, "hospitals/dashboard.html", context)


# =====================================
# 🧾 SUBMIT CLAIM (Hospital Users)
# =====================================
@login_required
@roles_required("hospital")
def submit_claim(request):
    """
    Allows hospital users to submit claims.
    """
    user = request.user
    hospital = getattr(user, "hospital_profile", None)

    if not hospital:
        messages.error(request, "Your hospital profile is missing.")
        return redirect("hospitals:hospital_list")

    if request.method == "POST":
        client_id = request.POST.get("client")
        policy_id = request.POST.get("policy")
        amount = request.POST.get("amount")

        if client_id and policy_id and amount:
            try:
                client = Client.objects.get(id=client_id)
                policy = Policy.objects.get(id=policy_id, active=True)
                claim_number = f"CLM-{timezone.now().strftime('%Y%m%d%H%M%S')}"

                Claim.objects.create(
                    claim_number=claim_number,
                    client=client,
                    policy=policy,
                    hospital=hospital,
                    amount=amount,
                    status="pending",
                    created_by=user,
                )
                messages.success(request, f"Claim {claim_number} submitted successfully.")
                return redirect("claims:hospital_claim_dashboard")

            except Client.DoesNotExist:
                messages.error(request, "Invalid client.")
            except Policy.DoesNotExist:
                messages.error(request, "Invalid policy.")
        else:
            messages.error(request, "All fields are required.")

    clients = Client.objects.all()
    policies = Policy.objects.filter(active=True)

    context = {
        "dashboard_title": "Submit New Claim",
        "user": user,
        "hospital": hospital,
        "clients": clients,
        "policies": policies,
    }
    return render(request, "hospitals/submit_claim.html", context)


# =====================================
# 🧭 ADMIN DASHBOARD (Modern)
# =====================================
@login_required
def admin_dashboard(request):
    """
    Modern analytics dashboard for Admins / Finance Officers.
    """
    user = request.user
    role = getattr(user, "role", "guest")

    if not (user.is_superuser or role in ["admin", "finance_officer"]):
        return redirect("accounts:dashboard")

    # ===== Statistics =====
    total_clients = Client.objects.count()
    total_policies = Policy.objects.count()
    total_claims = Claim.objects.count()
    total_hospitals = Hospital.objects.count()
    total_revenue = Policy.objects.aggregate(
        total=Coalesce(Sum(F("premium"), output_field=FloatField()), 0.0)
    )["total"]

    # ===== Dashboard Cards =====
    cards = [
        {"label": "Clients", "value": total_clients, "color": "blue"},
        {"label": "Policies", "value": total_policies, "color": "green"},
        {"label": "Claims", "value": total_claims, "color": "yellow"},
        {"label": "Hospitals", "value": total_hospitals, "color": "red"},
        {"label": "Revenue", "value": f"${total_revenue:,.2f}", "color": "purple"},
    ]

    # ===== Shortcuts =====
    shortcuts = [
        {"name": "Add Client", "url": "/clients/add/", "color": "blue"},
        {"name": "Add Policy", "url": "/policies/add/", "color": "green"},
        {"name": "Manage Claims", "url": "/claims/", "color": "yellow"},
        {"name": "Manage Hospitals", "url": "/hospitals/", "color": "red"},
    ]

    # ===== Charts =====
    policies_labels = list(Policy.objects.values_list("type", flat=True).distinct())
    policies_data = [Policy.objects.filter(type=t).count() for t in policies_labels]

    claims_labels = ["Pending", "Approved", "Rejected"]
    claims_data = [
        Claim.objects.filter(status="pending").count(),
        Claim.objects.filter(status="approved").count(),
        Claim.objects.filter(status="rejected").count(),
    ]

    hospitals_labels = ["Verified", "Unverified"]
    hospitals_data = [
        Hospital.objects.filter(verified=True).count(),
        Hospital.objects.filter(verified=False).count(),
    ]

    context = {
        "dashboard_title": "Admin Dashboard",
        "user": user,
        "role": role,
        "cards": cards,
        "shortcuts": shortcuts,
        "policies_labels": json.dumps(policies_labels),
        "policies_data": json.dumps(policies_data),
        "claims_labels": json.dumps(claims_labels),
        "claims_data": json.dumps(claims_data),
        "hospitals_labels": json.dumps(hospitals_labels),
        "hospitals_data": json.dumps(hospitals_data),
    }

    return render(request, "dashboard/dashboard.html", context)
