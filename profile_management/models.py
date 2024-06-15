from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import Group
# from .permissions import FREELANCE_PERMISSIONS, SPONSOR_PERMISSIONS, ADMIN_PERMISSIONS

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class FreelancerProfile(Profile):
    pass
    
class SponsorProfile(Profile):
    pass

class AdminProfile(Profile):
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