from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from profile_management.serializers import DocumentationRegisterSerializer
from profile_management.views import registerUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes

from skill_africa.permissions import IsAuthenticatedWithJWT
from freelancer_management.serializers import (
    FreelanceSerializer,
    FreelanceProfileSerializer,
)
from freelancer_management.models import FreelancerProfile
from freelancer_management.filters import CustomOrderingFilter, CustomSearchFilter
from skill_africa.utils import (
    delete_file_from_cloudinary,
    upload_file_to_cloudinary,
)


def get_freelancer_profile_with_uuid(uuid):
    return get_object_or_404(
        FreelancerProfile.objects.select_related("user"), user__uuid=uuid
    )


# Class View for registering Freelancers
class FreelanceRegistrationView(APIView):
    """
    Register a new Freelancers
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
        description="Register a new Freelancer",
        summary="Create a new Freelancer account",
    )
    def post(self, request):
        try:
            user, data = registerUser(self, request, "freelancer")  # Register user
            serializer = FreelanceSerializer(
                data={}
            )  # Then create a profile for the user
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


class FreelancerProfileList(generics.ListAPIView):
    queryset = FreelancerProfile.objects.all()
    serializer_class = FreelanceProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedWithJWT]
    filter_backends = [CustomSearchFilter, CustomOrderingFilter]
    ordering_fields = ["user__username"]
    ordering = ["user__username"]
    search_fields = [
        "user__username",
        "user__email",
        "niche__name",
        "first_name",
        "last_name",
    ]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a freelancer profile",
        description="Retrieve the details of a freelancer profile by UUID.",
        responses={200: FreelanceProfileSerializer},
    ),
    put=extend_schema(
        summary="Update a freelancer profile",
        description="Update the details of a freelancer profile by UUID. The requesting user must be the owner of the profile.",
        request=FreelanceProfileSerializer,
        responses={
            200: FreelanceProfileSerializer,
            403: OpenApiResponse(
                description="You do not have permission to update this profile"
            ),
            400: OpenApiResponse(description="Invalid data"),
        },
    ),
    delete=extend_schema(
        summary="Delete a freelancer profile",
        description="Delete a freelancer profile by UUID. The requesting user must be the owner of the profile.",
        responses={
            204: OpenApiResponse(description="Profile deleted successfully"),
            403: OpenApiResponse(
                description="You do not have permission to delete this profile"
            ),
        },
    ),
)
class FreelancerProfileDetail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedWithJWT]

    def get_object(self, uuid):
        return get_freelancer_profile_with_uuid(uuid)

    def get(self, request, uuid):
        profile = self.get_object(uuid)
        serializer = FreelanceProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, uuid):
        profile = self.get_object(uuid)
        if profile.user != request.user:
            return Response(
                {"error": "You do not have permission to update this profile"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = FreelanceProfileSerializer(profile, data=request.data)
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
