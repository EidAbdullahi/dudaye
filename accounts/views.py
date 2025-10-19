from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from rest_framework import viewsets, permissions
import json

# Import models
from .models import User
from .serializers import UserSerializer
from clients.models import Client
from policies.models import Policy
from claims.models import Claim
from hospitals.models import Hospital


# =========================
# 🌐 API ViewSet
# =========================
class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for managing users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    """Handles user authentication and redirects to role-specific dashboards"""
    if request.user.is_authenticated:
        # Redirect already logged-in users to their dashboard
        role = getattr(request.user, "role", None)
        if role == "admin" or request.user.is_superuser:
            return redirect('hospitals:hospital_list')  # Admin/Finance dashboard
        elif role == "finance_officer":
            return redirect('hospitals:hospital_list')
        elif role == "hospital":
            return redirect('hospitals:dashboard')       # Hospital user dashboard
        else:
            return redirect('accounts:dashboard')       # Default

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

                # Redirect based on role
                role = getattr(user, "role", None)
                if role == "admin" or user.is_superuser:
                    return redirect('hospitals:hospital_list')
                elif role == "finance_officer":
                    return redirect('hospitals:hospital_list')
                elif role == "hospital":
                    return redirect('hospitals:dashboard')
                else:
                    return redirect('accounts:dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "registration/login.html")



# =========================
# 🚪 LOGOUT VIEW
# =========================
@login_required(login_url="accounts:login")
def logout_view(request):
    """Logs the user out and redirects to login"""
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect("accounts:login")


# =========================
# 🧭 DASHBOARD VIEW
# =========================
@login_required(login_url="accounts:login")
def dashboard(request):
    """Main dashboard with analytics and quick actions"""
    user = request.user

    # Ensure superusers have full access
    if user.is_superuser:
        role = "admin"
    else:
        role = getattr(user, "role", "guest")

    # ===== Stats Summary =====
    total_clients = Client.objects.count()
    active_policies = Policy.objects.filter(active=True).count()
    total_claims = Claim.objects.count()
    total_hospitals = Hospital.objects.count()
    total_revenue = Policy.objects.filter(active=True).aggregate(total=Sum("premium"))["total"] or 0

    # ===== Dashboard Cards =====
    cards = [
        {"label": "Clients", "value": total_clients, "color": "blue"},
        {"label": "Active Policies", "value": active_policies, "color": "green"},
        {"label": "Claims", "value": total_claims, "color": "yellow"},
        {"label": "Hospitals", "value": total_hospitals, "color": "red"},
        {"label": "Revenue", "value": f"${total_revenue:,.2f}", "color": "purple"},
    ]

    # ===== Admin Shortcuts =====
    shortcuts = []
    if role == "admin":
        shortcuts = [
            {"name": "➕ Add Client", "url": "/clients/add/", "color": "blue"},
            {"name": "📑 Add Policy", "url": "/policies/add/", "color": "green"},
            {"name": "💰 Manage Claims", "url": "/claims/", "color": "yellow"},
            {"name": "🏥 Manage Hospitals", "url": "/hospitals/", "color": "red"},
        ]

    # ===== Chart Data =====
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

    # ===== Context =====
    context = {
        "dashboard_title": "Health Insurance Dashboard",
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