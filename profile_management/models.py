import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomPermission(Permission):
    class Meta:
        proxy = True
        
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('freelancer', 'Freelancer'),
        ('sponsor', 'Sponsor'),
        ('admin', 'Admin'),
    ]

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='freelancer')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    user_permissions = models.ManyToManyField(
        CustomPermission,
        verbose_name=('user permissions'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    def __str__(self):
        return self.username

class ProfileBase(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class FreelancerProfile(ProfileBase):
    pass
    
class SponsorProfile(ProfileBase):
    pass

class AdminProfile(ProfileBase):
    pass
    # Newly Registered admin should be approved by existing Admin first to get admin privileges.
    # Or alternatively we can make admin registeration a protected route. So that only an admin can register a new admin account.
    # Todo: Disscuss the above with team lead
    # verified = models.BooleanField(default=False) 



























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