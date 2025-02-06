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


class Language(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class FreelancerProfile(ProfileBase):
    bio = models.CharField(max_length=60, blank=True, null=True)
    about_me = models.TextField(max_length=1200, blank=True, null=True)
    location = models.CharField(max_length=300, blank=True, null=True)
    profile_pic = models.URLField(null=True, blank=True)
    profile_pic_public_id = models.CharField(max_length=255, blank=True, null=True)
    resume = models.URLField(null=True, blank=True)
    resume_public_id = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class FreelancerNiche(models.Model):
    freelancer = models.ForeignKey(
        FreelancerProfile, on_delete=models.CASCADE, related_name="niches"
    )
    niche = models.ForeignKey(Niche, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("freelancer", "niche")

    def __str__(self):
        return f"{self.freelancer.user.username} - {self.niche.name}"


class FreelancerLanguage(models.Model):
    freelancer = models.ForeignKey(
        FreelancerProfile, on_delete=models.CASCADE, related_name="languages"
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("freelancer", "language")

    def __str__(self):
        return f"{self.freelancer.user.username} - {self.language.name}"


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


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    freelancer = models.ForeignKey(
        FreelancerProfile, on_delete=models.CASCADE, related_name="projects"
    )
    image = models.URLField(null=True, blank=True)
    image_public_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    skills = models.CharField(max_length=255, default="")
    description = models.TextField(default="")
    tools = models.CharField(max_length=255, default="")
    url = models.URLField()

    def __str__(self):
        return f"{self.freelancer.username} - {self.name}"


class WorkExperience(models.Model):
    id = models.AutoField(primary_key=True)
    freelancer = models.ForeignKey(
        FreelancerProfile, on_delete=models.CASCADE, related_name="work_experiences"
    )
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    company_url = models.URLField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_role = models.BooleanField(default=False)
    description = models.TextField(max_length=2000)

    def __str__(self):
        return f"{self.freelancer.username} - {self.name}"
