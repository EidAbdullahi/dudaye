from django.db import models
from django.contrib.auth import get_user_model
from clients.models import Client

User = get_user_model()

class Policy(models.Model):
    POLICY_TYPE = [
        ('health', 'Health'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='policies')
    policy_number = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=POLICY_TYPE, default='health')
    start_date = models.DateField()
    end_date = models.DateField()
    premium = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_policies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.policy_number} ({self.client})"

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Policies"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
    paid_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.client} - {self.policy.policy_number} - {self.amount}"
