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


class FreelancerLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerLink
        fields = ["id", "name", "icon", "url"]


# In order to not change the above serializer drastically and break existing code
# Serializer for returning profile list and details
class FreelanceProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for freelancers.
    """

    user = UserDetailsSerializer(read_only=True)
    niche = serializers.PrimaryKeyRelatedField(queryset=Niche.objects.all())

    class Meta:
        model = FreelancerProfile
        depth = 1
        fields = [
            "id",
            "user",
            "bio",
            "niche",
            "profile_pic",
            "first_name",
            "last_name",
            "links",
            "skills",
            "created_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["niche"] = NicheSerializer(instance.niche).data
        representation["skills"] = ListFreelancerSkillSerializer(
            instance.skills, many=True
        ).data
        return representation


class NicheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Niche
        fields = ["id", "name"]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]


class FreelancerSkillSerializer(serializers.ModelSerializer):
    freelancer = FreelanceProfileSerializer(read_only=True)
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = FreelancerSkill
        fields = ["id", "freelancer", "skill"]


# For use in the FreelanceProfileSerializer
class ListFreelancerSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerSkill
        fields = ["skill"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["skill"] = SkillSerializer(instance.skill).data["name"]
        return representation
