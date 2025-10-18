from django.db import models
from policies.models import Policy

class Claim(models.Model):
    CLAIM_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    claim_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=CLAIM_STATUS, default='pending')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Claim {self.id} - {self.policy.policy_number}"
