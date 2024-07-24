# from django.contrib.auth.models import Permission

# """
# permissions.py

# This file contains all the custom permissions used in the application.
# When creating a new permission, add it to the appropriate array below.

# Permissions:
# Below is how permissions are to be created, take note of the created on the left side of the 
# left side of the assignment sign. Content type is always none.
#     place_holder, created = Permission.objects.get_or_create(
#         codename='placeholder_permission',
#         defaults={
#             'name': 'Placeholder Permission Should be removed when real permisssions are added',
#             'content_type': None
#         }
#     )

# Arrays:
#     - `DEFAULT_PERMISSIONS`: Permissions that they all share
#     - `FREELANCE_PERMISSIONS`: Permissions related to the freelancers
#     - `SPONSOR_PERMISSIONS`: Permissions related to sponsors
#     - `ADMIN_PERMISSIONS`: Permissions related to user admins

# Example:
#     To add a new permission to the freelancer, simply append it to the `FREELANCE_PERMISSIONS` array:
#         FREELANCE_PERMISSIONS = [
#             view_profile,
#             edit_profile,
#             new_permission_here  # Add your new permission here
#         ]
# """

# # Default Permissions
# place_holder, created = Permission.objects.get_or_create(
#     codename='placeholder_permission',
#     defaults={
#         'name': 'Placeholder Permission Should be removed when real permisssions are added',
#         'content_type': None
#     }
# )
# DEFAULT_PERMISSIONS=[place_holder]

# # Freelancer Permissions
# FREELANCE_PERMISSIONS = DEFAULT_PERMISSIONS + []

# # Sponsor Permissions
# SPONSOR_PERMISSIONS = DEFAULT_PERMISSIONS + []

# # Admin Permissions
# ADMIN_PERMISSIONS = DEFAULT_PERMISSIONS + []