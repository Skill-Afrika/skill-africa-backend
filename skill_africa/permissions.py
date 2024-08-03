from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication


class IsAuthenticatedWithJWT(BasePermission):
    def has_permission(self, request, view):
        auth = JWTAuthentication()
        auth_details = auth.authenticate(request)
        if auth_details is None:
            return False

        if auth_details[0] is not None and auth_details[1] is not None:
            return True
        return False
