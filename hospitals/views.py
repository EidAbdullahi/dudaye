from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import viewsets, permissions

from .models import Hospital
from .serializers import HospitalSerializer
from clients.models import Client
from policies.models import Policy
from claims.models import Claim
from accounts.utils import roles_required

User = get_user_model()

# ==============================
# 🌐 DRF API ViewSet
# ==============================
class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all().order_by('-created_at')
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated]


# ==============================
# 🌍 Web Views
# ==============================
@login_required
def hospital_list(request):
    """
    Display hospitals depending on user role:
    - Admin / Superuser / Finance Officer: All hospitals (newest first)
    - Others: Verified only
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
    Add or Edit Hospital
    Automatically creates a user for new hospitals.
    """
    hospital = None
    if pk:
        hospital = get_object_or_404(Hospital, pk=pk)

    if request.method == "POST":
        data = request.POST
        image = request.FILES.get("image")

        required_fields = ["name", "owner_first_name", "owner_last_name", "email"]
        if not hospital:
            # For new hospital, username and password are required
            required_fields += ["username", "password"]

        if all(data.get(f) for f in required_fields):
            if hospital:
                # Edit existing hospital
                for field in ["name", "owner_first_name", "owner_last_name", "email",
                              "mobile", "phone", "address", "city", "country",
                              "language", "currency"]:
                    setattr(hospital, field, data.get(field, getattr(hospital, field)))
                hospital.verified = data.get("verified") == "on"
                if image:
                    hospital.image = image
                hospital.save()
                messages.success(request, f"Hospital '{hospital.name}' updated successfully.")
            else:
                # Create user account for hospital
                username = data.get("username")
                password = data.get("password")
                if User.objects.filter(username=username).exists():
                    messages.error(request, f"Username '{username}' is already taken.")
                    return redirect("hospitals:hospital_form")

                user = User.objects.create(
                    username=username,
                    email=data.get("email"),
                    password=make_password(password),
                    role="hospital",
                    is_active=True,
                )

                # Create hospital profile
                Hospital.objects.create(
                    user=user,
                    name=data.get("name"),
                    owner_first_name=data.get("owner_first_name"),
                    owner_last_name=data.get("owner_last_name"),
                    email=data.get("email"),
                    mobile=data.get("mobile"),
                    phone=data.get("phone"),
                    address=data.get("address"),
                    city=data.get("city"),
                    country=data.get("country"),
                    language=data.get("language") or "English",
                    currency=data.get("currency") or "USD",
                    verified=data.get("verified") == "on",
                    image=image,
                )

                messages.success(request, f"Hospital '{data.get('name')}' added successfully with username '{username}'.")

            return redirect("hospitals:hospital_list")
        else:
            messages.error(request, "Please fill all required fields.")

    return render(request, "hospitals/hospital_form.html", {
        "hospital": hospital,
        "dashboard_title": "Edit Hospital" if hospital else "Add New Hospital",
        "role": request.user.role,
    })


@login_required
@roles_required("hospital")
def hospital_dashboard(request):
    """
    Hospital dashboard: shows submitted claims & quick actions
    Only for hospital users.
    """
    user = request.user
    hospital = getattr(user, "hospital_profile", None)
    if not hospital:
        messages.error(request, "Your hospital profile is missing. Contact admin.")
        return redirect("hospitals:hospital_list")

    claims = Claim.objects.filter(hospital=hospital).order_by('-created_at')

    context = {
        "dashboard_title": "Hospital Dashboard",
        "user": user,
        "role": user.role,
        "hospital": hospital,
        "claims": claims,
    }
    return render(request, "hospitals/dashboard.html", context)


@login_required
@roles_required("hospital")
def submit_claim(request):
    """
    Allows hospital users to submit claims for assigned clients.
    """
    user = request.user
    hospital = getattr(user, "hospital_profile", None)
    if not hospital:
        messages.error(request, "Your hospital profile is missing. Contact admin.")
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
                return redirect("hospitals:dashboard")

            except Client.DoesNotExist:
                messages.error(request, "Selected client does not exist.")
            except Policy.DoesNotExist:
                messages.error(request, "Selected policy does not exist.")
        else:
            messages.error(request, "All fields are required.")

    # Filter only clients assigned to this hospital
    clients = Client.objects.filter(agent__assigned_clients__hospital=hospital).distinct()
    policies = Policy.objects.filter(active=True)

    context = {
        "dashboard_title": "Submit New Claim",
        "user": user,
        "role": user.role,
        "hospital": hospital,
        "clients": clients,
        "policies": policies,
    }
    return render(request, "hospitals/submit_claim.html", context)
