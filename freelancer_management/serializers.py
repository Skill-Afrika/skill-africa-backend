from rest_framework import serializers
from profile_management.serializers import UserDetailsSerializer
from .models import Niche, Skill, FreelancerProfile, FreelancerSkill, FreelancerLink


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


# In order to not change the above serializer drastically and break existing code
# Serializer for returning profile list and details
class FreelanceProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for freelancers.
    """

    user = UserDetailsSerializer(read_only=True)

    class Meta:
        model = FreelancerProfile
        exclude = ["provider", "provider_id", "id"]
        depth = 1


class NicheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Niche
        fields = ["id", "name"]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]


class FreelancerSkillSerializer(serializers.ModelSerializer):
    freelancer = FreelanceSerializer(read_only=True)
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = FreelancerSkill
        fields = ["id", "freelancer", "skill"]


class FreelancerLinkSerializer(serializers.ModelSerializer):
    freelancer = FreelanceSerializer(read_only=True)

    class Meta:
        model = FreelancerLink
        fields = ["id", "freelancer", "name", "icon", "url"]
