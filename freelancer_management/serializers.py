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
    niches = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    skills = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    languages = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    links = FreelancerLinkSerializer(many=True, required=False)

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

    def update(self, instance, validated_data):
        niches_data = validated_data.pop("niches", [])
        skills_data = validated_data.pop("skills", [])
        languages_data = validated_data.pop("languages", [])
        links_data = validated_data.pop("links", [])
        errors = []

        # Update freelancer profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update niches
        if niches_data:
            # To make sure the user does not add more than 3 niches
            niche_id_number = len(niches_data)
            niche_number = len(FreelancerNiche.objects.filter(freelancer=instance))
            total_niches = niche_id_number + niche_number
            if total_niches > 3:
                errors.append("Maximum of 3 Niches Per user.")
            for niche_id in niches_data:
                try:
                    niche = Niche.objects.get(id=niche_id)
                    FreelancerNiche.objects.get_or_create(
                        freelancer=instance, niche=niche
                    )
                except Niche.DoesNotExist:
                    errors.append(f"Niche with id {niche_id} does not exist.")
                except Exception as e:
                    errors.append(str(e))

        # Update skills
        if skills_data:
            for skill_id in skills_data:
                try:
                    skill = Skill.objects.get(id=skill_id)
                    FreelancerSkill.objects.get_or_create(
                        freelancer=instance, skill=skill
                    )
                except Skill.DoesNotExist:
                    errors.append(f"Skill with id {skill_id} does not exist.")
                except Exception as e:
                    errors.append(str(e))

        # Update languages
        if languages_data:
            for language_id in languages_data:
                try:
                    language = Language.objects.get(id=language_id)
                    FreelancerLanguage.objects.get_or_create(
                        freelancer=instance, language=language
                    )
                except Language.DoesNotExist:
                    errors.append(f"Language with id {language_id} does not exist.")
                except Exception as e:
                    errors.append(str(e))

        # Update links
        if links_data:
            for link_data in links_data:
                FreelancerLink.objects.create(freelancer=instance, **link_data)

        # Raise ValidationError if errors occurred
        if errors:
            raise serializers.ValidationError({"errors": errors})

        return instance


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
        fields = [
            "id",
            "name",
            "url",
            "freelancer",
            "skills",
            "tools",
            "description",
            "image",
            "image_public_id",
        ]


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = "__all__"
