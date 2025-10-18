from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework import viewsets, permissions

from .models import Claim
from .serializers import ClaimSerializer
from clients.models import Client
from policies.models import Policy
from accounts.utils import roles_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Claim
from clients.models import Client
from policies.models import Policy
from hospitals.models import Hospital
from accounts.utils import roles_required

# -----------------------
# List claims
# -----------------------
@login_required
def claim_list(request):
    user = request.user
    role = getattr(user, "role", "guest")

    if role in ["admin", "claim_officer"]:
        claims = Claim.objects.all()
        title = "All Claims"
    elif role == "agent":
        claims = Claim.objects.filter(client__agent=user)
        title = "My Clients' Claims"
    elif role == "hospital":
        hospital = getattr(user, "hospital_profile", None)
        claims = Claim.objects.filter(hospital=hospital) if hospital else Claim.objects.none()
        title = "My Hospital Claims"
    else:
        claims = Claim.objects.none()
        title = "Claims"

    return render(request, "claims/claim_list.html", {
        "claims": claims,
        "dashboard_title": title,
        "role": role,
    })


# -----------------------
# Add claim (Hospital only)
# -----------------------
@login_required
@roles_required("hospital")
def add_claim(request):
    user = request.user
    hospital = getattr(user, "hospital_profile", None)
    if not hospital:
        messages.error(request, "Your hospital profile is missing.")
        return redirect("claims:claim_list")

    if request.method == "POST":
        client_id = request.POST.get("client")
        policy_id = request.POST.get("policy")
        amount = request.POST.get("amount")
        notes = request.POST.get("notes", "")

        if client_id and policy_id and amount:
            client = get_object_or_404(Client, id=client_id)
            policy = get_object_or_404(Policy, id=policy_id, active=True)

            claim_number = f"CLM-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            Claim.objects.create(
                claim_number=claim_number,
                client=client,
                policy=policy,
                hospital=hospital,
                amount=amount,
                status="pending",
                notes=notes,
                created_by=user,
            )
            messages.success(request, f"Claim {claim_number} submitted successfully.")
            return redirect("claims:claim_list")
        else:
            messages.error(request, "All fields are required.")

    clients = Client.objects.filter(agent__isnull=False)  # assigned clients
    policies = Policy.objects.filter(active=True)

    return render(request, "claims/add_claim.html", {
        "dashboard_title": "Submit New Claim",
        "clients": clients,
        "policies": policies,
    })


# -----------------------
# Claim detail
# -----------------------
@login_required
def claim_detail(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    return render(request, "claims/claim_detail.html", {
        "claim": claim,
        "dashboard_title": f"Claim Details - {claim.claim_number}",
        "role": getattr(request.user, "role", "guest"),
    })


# -----------------------
# Edit claim (Admin / Claim Officer)
# -----------------------
@login_required
@roles_required("admin", "claim_officer")
def edit_claim(request, pk):
    claim = get_object_or_404(Claim, pk=pk)

    if request.method == "POST":
        claim.amount = request.POST.get("amount", claim.amount)
        claim.notes = request.POST.get("notes", claim.notes)
        claim.status = request.POST.get("status", claim.status)
        claim.save()
        messages.success(request, f"Claim {claim.claim_number} updated.")
        return redirect("claims:claim_list")

    return render(request, "claims/add_claim.html", {
        "dashboard_title": f"Edit Claim - {claim.claim_number}",
        "claim": claim,
        "clients": [claim.client],
        "policies": [claim.policy],
    })


# -----------------------
# Approve claim
# -----------------------
@login_required
@roles_required("admin", "claim_officer")
def approve_claim(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    claim.status = "approved"
    claim.save()
    messages.success(request, f"Claim {claim.claim_number} approved.")
    return redirect("claims:claim_list")


# -----------------------
# Reject claim
# -----------------------
@login_required
@roles_required("admin", "claim_officer")
def reject_claim(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    claim.status = "rejected"
    claim.save()
    messages.success(request, f"Claim {claim.claim_number} rejected.")
    return redirect("claims:claim_list")

# ==============================
# 🌐 DRF API ViewSet
# ==============================
class ClaimViewSet(viewsets.ModelViewSet):
    """
    REST API endpoint for managing claims.
    Only authenticated users can access.
    Role-based filtering applied.
    """
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", "guest")

        if user.is_superuser or role in ["admin", "claim_officer"]:
            return Claim.objects.all()
        elif role == "agent":
            return Claim.objects.filter(client__agent=user)
        elif role == "hospital":
            hospital = getattr(user, "hospital_profile", None)
            return Claim.objects.filter(hospital=hospital) if hospital else Claim.objects.none()
        return Claim.objects.none()



