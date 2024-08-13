from rest_framework import permissions
from django.contrib.auth.models import Permission

class IsAdmin(permissions.BasePermission):
    """
    custom permission to allow only Admin to some views
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
    
