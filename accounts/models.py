from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model with role-based access for Health Insurance platform.
    Admins can suspend users, assign roles, and manage access.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('agent', 'Agent'),
        ('policyholder', 'Policyholder'),
        ('claim_officer', 'Claim Officer'),
        ('finance_officer', 'Finance Officer'),
        ('report_officer', 'Report Officer'),
        ('hospital', 'Hospital'),
    ]

    # -------------------------
    # Core fields
    # -------------------------
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='policyholder',
        help_text="Role of the user in the system"
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # -------------------------
    # Status flags
    # -------------------------
    is_suspended = models.BooleanField(
        default=False,
        help_text="Designates whether this user is suspended."
    )

    # -------------------------
    # String representation
    # -------------------------
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    # =========================
    # 🛠️ Admin utility methods
    # =========================
    def suspend(self):
        """Suspend this user (cannot log in)."""
        self.is_suspended = True
        self.save(update_fields=['is_suspended'])

    def activate(self):
        """Activate (unsuspend) this user."""
        self.is_suspended = False
        self.save(update_fields=['is_suspended'])

    def is_active_for_login(self):
        """
        Check if the user can log in.
        Returns True only if the user is active and not suspended.
        """
        return self.is_active and not self.is_suspended

    # =========================
    # 🧠 Smart Default Logic
    # =========================
    def save(self, *args, **kwargs):
        """
        Automatically assign the correct role for superusers.
        Ensures no superuser is incorrectly labeled as 'Policyholder'.
        """
        if self.is_superuser and self.role != "admin":
            self.role = "admin"
        super().save(*args, **kwargs)
