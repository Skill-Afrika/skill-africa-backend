from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from profile_management.serializers import DocumentationRegisterSerializer
from profile_management.views import registerUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse

from .models import AdminProfile
from .filters import CustomOrderingFilter, CustomSearchFilter
from .serializers import AdminProfileSerializer, AdminSerializer
from profile_management.serializers import DocumentationRegisterSerializer
from profile_management.views import registerUser
from skill_africa.permissions import IsAuthenticatedWithJWT


# Class View for registering Admins
def get_admin_profile_with_uuid(uuid):
    return get_object_or_404(
        AdminProfile.objects.select_related("user"), user__uuid=uuid
    )


class AdminRegistrationView(APIView):
    """
    Register a new Admins
    """

    @extend_schema(
        request=DocumentationRegisterSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string"},
                            "email": {"type": "string"},
                        },
                    },
                    "refresh": {"type": "string"},
                    "access": {"type": "string"},
                },
                "examples": [
                    {
                        "summary": "Successful registration",
                        "value": {
                            "user": {
                                "username": "john_doe",
                                "email": "johndoe@example.com",
                            },
                            "refresh": "refresh_token_here",
                            "access": "access_token_here",
                        },
                    }
                ],
            },
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        description="Register a new Admin",
        summary="Create a new Admin account",
    )
    def post(self, request):
        try:
            user, data = registerUser(self, request, "admin")  # Register user
            serializer = AdminSerializer(data={})  # Then create a profile for the user
            serializer.is_valid(raise_exception=True)
            serializer.create(validated_data={"user": user})
        except ValidationError as e:
            error_details = {"error": {}}
            for key in e.detail.keys():
                error_details["error"][key] = e.detail[key][0]

            return Response(data=error_details, status=status.HTTP_400_BAD_REQUEST)

        if data:
            response = Response(data, status=status.HTTP_201_CREATED)
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT)
        return response


class AdminProfileList(generics.ListAPIView):
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedWithJWT]
    filter_backends = [CustomSearchFilter, CustomOrderingFilter]
    ordering_fields = ["user__username"]
    ordering = ["user__username"]
    search_fields = [
        "user__username",
        "user__email",
        "first_name",
        "last_name",
    ]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a Admin profile",
        description="Retrieve the details of an admin's profile by UUID.",
        responses={200: AdminProfileSerializer},
    ),
    put=extend_schema(
        summary="Update an Admin profile",
        description="Update the details of an Admin profile by UUID. The requesting user must be the owner of the profile.",
        request=AdminProfileSerializer,
        responses={
            200: AdminProfileSerializer,
            403: OpenApiResponse(
                description="You do not have permission to update this profile"
            ),
            400: OpenApiResponse(description="Invalid data"),
        },
    ),
    delete=extend_schema(
        summary="Delete an Admin profile",
        description="Delete an Admin profile by UUID. The requesting user must be the owner of the profile.",
        responses={
            204: OpenApiResponse(description="Profile deleted successfully"),
            403: OpenApiResponse(
                description="You do not have permission to delete this profile"
            ),
        },
    ),
)
class AdminProfileDetail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedWithJWT]

    def get_object(self, uuid):
        return get_admin_profile_with_uuid(uuid)

    def get(self, request, uuid):
        profile = self.get_object(uuid)
        serializer = AdminProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, uuid):
        profile = self.get_object(uuid)
        if profile.user != request.user:
            return Response(
                {"error": "You do not have permission to update this profile"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AdminProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):
        profile = self.get_object(uuid)
        if profile.user != request.user:
            return Response(
                {"error": "You do not have permission to delete this profile"},
                status=status.HTTP_403_FORBIDDEN,
            )

        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
