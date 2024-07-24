from rest_framework import serializers
from .models import FreelancerProfile


class FreelanceSerializer(serializers.ModelSerializer):
    """
    Serializer for freelancers.
    """

    class Meta:
        model = FreelancerProfile
        fields = "__all__"
        depth = 1
        extra_kwargs = {
            "provider_id": {"required": False},
        }
