from django.db import models
from profile_management.models import ProfileBase


class Niche(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class FreelancerProfile(ProfileBase):
    bio = models.TextField(max_length=300, blank=True, null=True)
    niche = models.ForeignKey(Niche, on_delete=models.SET_NULL, null=True)
    profile_pic = models.URLField(null=True, blank=True)  # Todo: Add cloudinary support
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class FreelancerSkill(models.Model):
    freelancer = models.ForeignKey(
        FreelancerProfile, on_delete=models.CASCADE, related_name="skills"
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("freelancer", "skill")

    def __str__(self):
        return f"{self.freelancer.user.username} - {self.skill.name}"


class FreelancerLink(models.Model):
    id = models.AutoField(primary_key=True)
    freelancer = models.ForeignKey(
        FreelancerProfile, on_delete=models.CASCADE, related_name="links"
    )
    name = models.CharField(max_length=255)
    icon = models.URLField(blank=True)
    url = models.URLField()

    def __str__(self):
        return f"{self.freelancer.username} - {self.name}"
