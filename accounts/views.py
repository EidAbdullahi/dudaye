from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, FloatField
from django.db.models.functions import Coalesce
from rest_framework import viewsets, permissions
import json

# Import your models
from .models import User
from .serializers import UserSerializer
from clients.models import Client
from policies.models import Policy
from claims.models import Claim
from hospitals.models import Hospital


# ============================================================
# 🌐 API ViewSet
# ============================================================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


# ============================================================
# 🔐 LOGIN VIEW
# ============================================================
def login_view(request):
    """Handles authentication and redirects based on user role"""
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            if not user.is_active or getattr(user, "is_suspended", False):
                messages.error(request, "Your account is inactive or suspended.")
            else:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")

                role = getattr(user, "role", None)
                if role == "hospital":
                    return redirect("claims:hospital_claim_dashboard")
                return redirect("accounts:dashboard")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "registration/login.html")


# ============================================================
# 🚪 LOGOUT VIEW
# ============================================================
@login_required(login_url="accounts:login")
def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect("accounts:login")


# ============================================================
# 🧭 ADMIN DASHBOARD VIEW
# ============================================================
@login_required(login_url="accounts:login")
def dashboard(request):
    """Admin/Finance dashboard view"""
    user = request.user
    role = getattr(user, "role", "guest")

    # === Stats ===
    total_clients = Client.objects.count()
    active_policies = Policy.objects.filter(active=True).count()
    total_claims = Claim.objects.count()
    total_hospitals = Hospital.objects.count()
    total_revenue = (
        Claim.objects.filter(status__in=["approved", "reimbursed"])
        .aggregate(total=Coalesce(Sum(F("amount"), output_field=FloatField()), 0.0))
        ["total"]
    )

    # === Cards ===
    cards = [
        {"label": "Clients", "value": total_clients, "color": "blue"},
        {"label": "Active Policies", "value": active_policies, "color": "green"},
        {"label": "Claims", "value": total_claims, "color": "yellow"},
        {"label": "Hospitals", "value": total_hospitals, "color": "red"},
        {"label": "Revenue Collected", "value": f"${total_revenue:,.2f}", "color": "teal"},
    ]

    # === Shortcuts ===
    shortcuts = []
    if role in ["admin", "finance_officer"] or user.is_superuser:
        shortcuts = [
            {"name": "👥 Manage Users", "url": "/accounts/users/", "color": "blue"},
            {"name": "➕ Add Client", "url": "/clients/add/", "color": "green"},
            {"name": "📑 Add Policy", "url": "/policies/add/", "color": "yellow"},
            {"name": "💰 Manage Claims", "url": "/claims/", "color": "purple"},
            {"name": "🏥 Manage Hospitals", "url": "/hospitals/", "color": "red"},
        ]

    # === Chart Data ===
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

    # === Context ===
    context = {
        "dashboard_title": "Admin Dashboard | HealthInsure",
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


# ============================================================
# 👥 USER MANAGEMENT
# ============================================================
@login_required(login_url="accounts:login")
def user_list(request):
    """Displays all users for admin"""
    if not request.user.is_superuser and getattr(request.user, "role", "") != "admin":
        messages.error(request, "You do not have permission to view this page.")
        return redirect("accounts:dashboard")

    users = User.objects.all().order_by("id")
    return render(request, "dashboard/user_list.html", {"users": users})


@login_required(login_url="accounts:login")
def toggle_user_status(request, user_id):
    """Activate or deactivate a user"""
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect("accounts:user_list")

    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f"User '{user.username}' status updated.")
    return redirect("accounts:user_list")
