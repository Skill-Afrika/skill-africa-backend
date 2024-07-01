from rest_framework import serializers
from .models import SponsorProfile

class SponsorSerializer(serializers.ModelSerializer):
    """
    Serializer for sponsors.
    """
    class Meta:
        model = SponsorProfile
        fields = '__all__'
        depth = 1