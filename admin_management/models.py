from django.db import models
from profile_management.models import ProfileBase


class AdminProfile(ProfileBase):
    bio = models.TextField(max_length=300, blank=True, null=True)
    profile_pic = models.URLField(null=True, blank=True)  # Todo: Add cloudinary support
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    # Newly Registered admin should be approved by existing Admin first to get admin privileges.
    # Or alternatively we can make admin registeration a protected route. So that only an admin can register a new admin account.
    # Todo: Disscuss the above with team lead
    # verified = models.BooleanField(default=False)
