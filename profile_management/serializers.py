from rest_framework import serializers
from .models import FreelancerProfile, SponsorProfile, AdminProfile

class FreelanceSerializer(serializers.ModelSerializer):
    """
    Serializer for freelancers.
    """
    class Meta:
        model = FreelancerProfile
        fields = '__all__'
        depth = 1


class SponsorSerializer(serializers.ModelSerializer):
    """
    Serializer for sponsors.
    """
    class Meta:
        model = SponsorProfile
        fields = '__all__'
        depth = 1


class AdminSerializer(serializers.ModelSerializer):
    """
    Serializer for admin.
    """
    class Meta:
        model = AdminProfile
        fields = '__all__'
        depth = 1