from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions

from .models import Claim
from .serializers import ClaimSerializer
from clients.models import Client
from policies.models import Policy
from accounts.utils import roles_required

# ==============================
# 🌐 API ViewSet (DRF)
# ==============================
class ClaimViewSet(viewsets.ModelViewSet):
    """
    REST API endpoint for managing claims.
    Only authenticated users can access.
    """
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]


# ==============================
# 🌍 Web Views
# ==============================
@login_required
@roles_required("admin", "claim_officer", "agent", "hospital")
def claim_list(request):
    """
    List claims based on role:
    - Admin / Superuser: All claims
    - Claim Officer: All claims
    - Agent: Only claims for their clients
    - Hospital: Only claims submitted by this hospital
    """
    user = request.user
    role = getattr(user, "role", "guest")

    if user.is_superuser or role == "admin" or role == "claim_officer":
        claims = Claim.objects.all()
        title = "All Claims"

    elif role == "agent":
        claims = Claim.objects.filter(client__agent=user)
        title = "Agent - My Clients' Claims"

    elif role == "hospital":
        claims = Claim.objects.filter(hospital=user.hospital_profile)
        title = "Hospital - Submitted Claims"

    context = {
        "claims": claims,
        "role": role,
        "user": user,
        "dashboard_title": title,
    }
    return render(request, "claims/claim_list.html", context)


@login_required
@roles_required("admin", "claim_officer", "hospital")
def add_claim(request):
    """
    Add new claim:
    - Admin / Claim Officer: Can add any claim
    - Hospital: Can add claims only for their own clients
    """
    user = request.user
    role = getattr(user, "role", "guest")

    if request.method == "POST":
        claim_number = request.POST.get("claim_number")
        client_id = request.POST.get("client")
        policy_id = request.POST.get("policy")
        amount = request.POST.get("amount")
        status = "pending"  # default

        if claim_number and client_id and policy_id and amount:
            try:
                client = Client.objects.get(id=client_id)
                policy = Policy.objects.get(id=policy_id)

                # Hospital can only submit for themselves
                hospital = user.hospital_profile if role == "hospital" else None

                Claim.objects.create(
                    claim_number=claim_number,
                    client=client,
                    policy=policy,
                    hospital=hospital,
                    amount=amount,
                    status=status,
                    created_by=user,
                )
                messages.success(request, f"Claim {claim_number} added successfully.")
                return redirect("claims:claim_list")
            except Client.DoesNotExist:
                messages.error(request, "Selected client does not exist.")
            except Policy.DoesNotExist:
                messages.error(request, "Selected policy does not exist.")
        else:
            messages.error(request, "Please fill all required fields.")

    clients = Client.objects.all()
    policies = Policy.objects.all()
    context = {
        "clients": clients,
        "policies": policies,
        "role": role,
        "dashboard_title": "Add New Claim",
    }
    return render(request, "claims/add_claim.html", context)


@login_required
@roles_required("admin", "claim_officer", "agent", "hospital")
def claim_detail(request, pk):
    """
    View a single claim based on role:
    - Admin / Superuser / Claim Officer: All claims
    - Agent: Only their clients’ claims
    - Hospital: Only their submitted claims
    """
    user = request.user
    role = getattr(user, "role", "guest")
    claim = get_object_or_404(Claim, pk=pk)

    # Restrict access for Agent & Hospital
    if role == "agent" and claim.client.agent != user:
        messages.error(request, "You are not authorized to view this claim.")
        return render(request, "403.html", status=403)

    if role == "hospital" and claim.hospital != user.hospital_profile:
        messages.error(request, "You are not authorized to view this claim.")
        return render(request, "403.html", status=403)

    context = {
        "claim": claim,
        "role": role,
        "dashboard_title": f"Claim #{claim.claim_number}",
    }
    return render(request, "claims/claim_detail.html", context)
