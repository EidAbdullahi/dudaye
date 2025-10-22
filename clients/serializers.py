import base64
from rest_framework import serializers
from .models import Client
# We’ll handle Base64 encoding for fingerprints in JSON. DRF doesn’t support raw binary well in JSON.
class ClientSerializer(serializers.ModelSerializer):
    fingerprint_data = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Client
        fields = [
            "id", "first_name", "last_name", "phone", "email",
            "dob", "gender", "address", "photo", "fingerprint_data",
            "status", "fingerprint_verified"
        ]
        read_only_fields = ["status", "fingerprint_verified"]

    def create(self, validated_data):
        fingerprint_b64 = validated_data.pop("fingerprint_data", None)
        client = Client.objects.create(**validated_data)

        if fingerprint_b64:
            client.fingerprint_data = base64.b64decode(fingerprint_b64)
            # Placeholder for verification logic
            client.fingerprint_verified = True  # Set False if verification fails
            client.status = "verified"
            client.save()
        return client
