from rest_framework import serializers
from profile_management.serializers import UserDetailsSerializer
from .models import (
    FreelancerLanguage,
    FreelancerNiche,
    Language,
    Niche,
    Project,
    Skill,
    FreelancerProfile,
    FreelancerSkill,
    FreelancerLink,
    WorkExperience,
)


def extract_values(ordered_dict_list, key):
    """
    Converts a list of OrderedDicts to a list of string values based on the specified key.

    :param ordered_dict_list: List of OrderedDict objects
    :param key: The key whose value needs to be extracted
    :return: List of string values
    """
    return [item[key] for item in ordered_dict_list if key in item]


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

    class Meta:
        model = FreelancerProfile
        depth = 1
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "bio",
            "about_me",
            "location",
            "profile_pic",
            "resume",
            "links",
            "skills",
            "niches",
            "languages",
            "created_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["niches"] = extract_values(
            ListFreelancerNicheSerializer(instance.niches, many=True).data, "niche"
        )
        representation["skills"] = extract_values(
            ListFreelancerSkillSerializer(instance.skills, many=True).data, "skill"
        )
        representation["languages"] = extract_values(
            ListFreelancerLanguageSerializer(instance.languages, many=True).data,
            "language",
        )
        return representation


class NicheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Niche
        fields = ["id", "name"]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "name"]


class FreelancerNicheSerializer(serializers.ModelSerializer):
    freelancer = FreelanceProfileSerializer(read_only=True)
    niche = NicheSerializer(read_only=True)

    class Meta:
        model = FreelancerNiche
        fields = ["id", "freelancer", "niche"]


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


class FreelancerLanguageSerializer(serializers.ModelSerializer):
    freelancer = FreelanceProfileSerializer(read_only=True)
    language = LanguageSerializer(read_only=True)

    class Meta:
        model = FreelancerLanguage
        fields = ["id", "freelancer", "language"]


# For use in the FreelanceProfileSerializer
class ListFreelancerLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerLanguage
        fields = ["language"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["language"] = LanguageSerializer(instance.language).data["name"]
        return representation


# For use in the FreelanceProfileSerializer
class ListFreelancerNicheSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerNiche
        fields = ["niche"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["niche"] = NicheSerializer(instance.niche).data["name"]
        return representation


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "url", "freelancer", "image", "image_public_id"]


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = "__all__"
