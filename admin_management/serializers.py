from rest_framework import serializers

from profile_management.serializers import UserDetailsSerializer
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


# In order to not change the above serializer drastically and break existing code
# Serializer for returning profile list and details
class AdminProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for freelancers.
    """

    user = UserDetailsSerializer(read_only=True)

    class Meta:
        model = AdminProfile
        depth = 1
        fields = [
            "id",
            "user",
            "profile_pic",
            "first_name",
            "last_name",
            "created_at",
        ]
