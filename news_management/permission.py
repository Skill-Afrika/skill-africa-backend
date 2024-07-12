from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    custom permission to allow only Admin to some views
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
    