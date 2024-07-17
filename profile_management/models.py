import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ("freelancer", "Freelancer"),
        ("sponsor", "Sponsor"),
        ("admin", "Admin"),
    ]

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="freelancer")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return self.username


class ProfileBase(models.Model):
    AUTH_CHOICES = [
        ("password", "Password"),
        ("google", "Google"),
        ("microsoft", "Microsoft"),
        ("github", "Github"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_method = models.CharField(
        max_length=10, choices=AUTH_CHOICES, default="password"
    )

    class Meta:
        abstract = True


class PasswordOTP(models.Model):
    """
    Model to store OTP for password reset
    """

    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.email}"


# # Get or create groups
# admin_group, created = Group.objects.get_or_create(name='Admin')
# freelancer_group, created = Group.objects.get_or_create(name='Freelancer')
# sponsor_group, created = Group.objects.get_or_create(name='Sponsor')

# # Assigning permisions to groups
# for permission in FREELANCE_PERMISSIONS:
#     freelancer_group.permissions.add(permission)

# for permission in SPONSOR_PERMISSIONS:
#     sponsor_group.permissions.add(permission)

# for permission in ADMIN_PERMISSIONS:
#     admin_group.permissions.add(permission)
