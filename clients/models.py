from django.db import models
from accounts.models import User
from django.conf import settings
from django.db import models


class Client(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Optional agent assigned
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients_assigned'
    )

    # Track who created this client
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients_created'
    )

    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
