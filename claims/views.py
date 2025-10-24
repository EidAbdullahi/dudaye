from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework import viewsets, permissions

from .models import Claim
from .serializers import ClaimSerializer
from clients.models import Client
from policies.models import Policy
from hospitals.models import Hospital
from accounts.utils import roles_required


# -----------------------
# 🏥 Hospital Claim Dashboard
# -----------------------
@login_required
@roles_required("hospital")
def hospital_claim_dashboard(request):
    """Dashboard for hospitals to view and manage their submitted claims."""
    user = request.user
    hospital = getattr(user, "hospital_profile", None)

    if not hospital:
        messages.error(request, "Hospital profile not found.")
        return redirect("accounts:dashboard")

    total_claims = Claim.objects.filter(hospital=hospital).count()
    pending_claims = Claim.objects.filter(hospital=hospital, status="pending").count()
    approved_claims = Claim.objects.filter(hospital=hospital, status="approved").count()
    rejected_claims = Claim.objects.filter(hospital=hospital, status="rejected").count()

    claims = Claim.objects.filter(hospital=hospital).select_related("client", "policy").order_by("-created_at")

    context = {
        "hospital": hospital,
        "dashboard_title": f"{hospital.name} Claims Dashboard",
        "total_claims": total_claims,
        "pending_claims": pending_claims,
        "approved_claims": approved_claims,
        "rejected_claims": rejected_claims,
        "claims": claims,
    }

    return render(request, "claims/hospital_dashboard.html", context)


# -----------------------
# 🧩 Claim List (all roles)
# -----------------------
@login_required
def claim_list(request):
    user = request.user
    role = getattr(user, "role", None)

    if user.is_superuser or role in ["admin", "claim_officer"]:
        claims = Claim.objects.select_related("client", "hospital", "policy").all()
        title = "All Hospital Claims"
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
# 🏥 Add Claim (Hospital)
# -----------------------
@login_required
@roles_required("hospital")
def add_claim(request):
    """Hospitals submit a new claim for a client with an active policy."""
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
            client = get_object_or_404(Client, pk=client_id)
            policy = get_object_or_404(Policy, pk=policy_id, is_active=True)

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

    clients = Client.objects.all()
    policies = Policy.objects.filter(is_active=True)

    return render(request, "claims/add_claim.html", {
        "dashboard_title": "Submit New Claim",
        "clients": clients,
        "policies": policies,
    })


# -----------------------
# ✏️ Edit Claim (Admin/Claim Officer)
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
        messages.success(request, f"Claim {claim.claim_number} updated successfully.")
        return redirect("claims:claim_list")

    return render(request, "claims/edit_claim.html", {
        "dashboard_title": f"Edit Claim - {claim.claim_number}",
        "claim": claim,
        "role": getattr(request.user, "role", "guest"),
    })


# -----------------------
# 🔍 Claim Detail
# -----------------------
@login_required
def claim_detail(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    user = request.user
    role = getattr(user, "role", None)

    if user.is_superuser:
        role = "admin"
    elif role == "hospital":
        hospital = getattr(user, "hospital_profile", None)
        if not hospital or claim.hospital != hospital:
            messages.error(request, "You are not authorized to view this claim.")
            return redirect("claims:claim_list")
    elif role == "agent":
        if claim.client.agent != user:
            messages.error(request, "You are not authorized to view this claim.")
            return redirect("claims:claim_list")
    elif role not in ["admin", "claim_officer"]:
        messages.error(request, "Access denied.")
        return redirect("claims:claim_list")

    return render(request, "claims/claim_detail.html", {
        "claim": claim,
        "dashboard_title": f"Claim Details - {claim.claim_number}",
        "role": role,
    })


# -----------------------
# ✅ Approve Claim
# -----------------------
@login_required
@roles_required("admin", "claim_officer")
def approve_claim(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    if claim.status != "approved":
        claim.status = "approved"
        claim.save()
        messages.success(request, f"Claim {claim.claim_number} approved successfully.")
    else:
        messages.info(request, f"Claim {claim.claim_number} is already approved.")
    return redirect("claims:claim_detail", pk=pk)


# -----------------------
# ❌ Reject Claim
# -----------------------
@login_required
@roles_required("admin", "claim_officer")
def reject_claim(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    if claim.status != "rejected":
        claim.status = "rejected"
        claim.save()
        messages.warning(request, f"Claim {claim.claim_number} rejected.")
    else:
        messages.info(request, f"Claim {claim.claim_number} is already rejected.")
    return redirect("claims:claim_detail", pk=pk)


# -----------------------
# 💰 Reimburse Claim
# -----------------------
@login_required
@roles_required("admin")
def reimburse_claim(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    if claim.status == "approved":
        claim.status = "reimbursed"
        claim.save()
        messages.success(request, f"Claim {claim.claim_number} marked as reimbursed.")
    else:
        messages.error(request, "Only approved claims can be reimbursed.")
    return redirect("claims:claim_detail", pk=pk)


# -----------------------
# 🌐 DRF API
# -----------------------
class ClaimViewSet(viewsets.ModelViewSet):
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
