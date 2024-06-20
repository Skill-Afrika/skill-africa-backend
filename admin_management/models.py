from profile_management.models import ProfileBase

class AdminProfile(ProfileBase):
    pass
    # Newly Registered admin should be approved by existing Admin first to get admin privileges.
    # Or alternatively we can make admin registeration a protected route. So that only an admin can register a new admin account.
    # Todo: Disscuss the above with team lead
    # verified = models.BooleanField(default=False) 