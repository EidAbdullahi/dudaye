from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile', null=True, blank=True)
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=100, default='English')
    owner_first_name = models.CharField(max_length=100)
    owner_last_name = models.CharField(max_length=100)
    email = models.EmailField()
    currency = models.CharField(max_length=10, default='USD')
    mobile = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='hospitals/', blank=True, null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name
