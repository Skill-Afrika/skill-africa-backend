from rest_framework import serializers
from .models import AdminProfile


class AdminSerializer(serializers.ModelSerializer):
    """
    Serializer for admin.
    """

    class Meta:
        model = AdminProfile
        fields = "__all__"
        depth = 1
        extra_kwargs = {
            "provider_id": {"required": False},
        }
