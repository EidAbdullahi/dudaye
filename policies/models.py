from django.db import models
from accounts.models import User
from clients.models import Client

class Policy(models.Model):
    POLICY_TYPE = [
        ("individual", "Individual"),
        ("family", "Family"),
        ("employer", "Employer Sponsored"),
        ("ngo", "NGO Supported"),
        ("health", "Health Policy"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="policies")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    policy_number = models.CharField(max_length=20, unique=True)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPE)
    coverage_details = models.TextField(blank=True, null=True)
    premium = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    start_date = models.DateField()
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    max_claim_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    waiting_period_days = models.PositiveIntegerField(default=0)
    deductible = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.policy_number} - {self.client.name}"

    class Meta:
        ordering = ["-created_at"]
