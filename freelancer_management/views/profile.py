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


@extend_schema(
    operation_id="profile_picture_upload",
    summary="Upload Profile Picture",
    description=(
        "Allows authenticated users to upload a profile picture for a freelancer using their UUID. "
        "The file must be an image (JPEG or PNG) and will replace any existing profile picture."
    ),
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "image": {
                    "type": "string",
                    "format": "binary",
                    "description": "Image file to be uploaded (JPEG or PNG only).",
                }
            },
            "required": ["image"],
        }
    },
    responses={
        201: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Successful Upload",
            value={
                "message": "File uploaded successfully",
                "profile_pic": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
            },
            status_codes=["201"],
        ),
        OpenApiExample(
            "Unsupported File Type",
            value={"error": "Unsupported file type"},
            status_codes=["400"],
        ),
        OpenApiExample(
            "Unauthorized User",
            value={"error": "User Unauthorized"},
            status_codes=["401"],
        ),
    ],
)
class ProfilePictureUploadView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]
    SUPPORTED_MIME_TYPES = ["image/jpeg", "image/png"]
    MAX_FILE_SIZE_MB = 5

    def post(self, request, uuid):
        try:
            file = request.FILES.get("image")
            freelancer = get_freelancer_profile_with_uuid(uuid)

            if not file:
                return Response(
                    {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the file type is supported
            if file.content_type not in self.SUPPORTED_MIME_TYPES:
                return Response(
                    {"error": "Unsupported file type"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check file size (convert MAX_FILE_SIZE_MB to bytes)
            max_file_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
            if file.size > max_file_size_bytes:
                return Response(
                    {
                        "error": f"File size exceeds the maximum limit of {self.MAX_FILE_SIZE_MB} MB."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if request.user != freelancer.user:
                return Response(
                    {"error": "User Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
                )

            # Delete any previous file
            if freelancer.profile_pic_public_id:
                delete_file_from_cloudinary(freelancer.profile_pic_public_id)

            # Upload the file to Cloudinary
            result = upload_file_to_cloudinary(file, folder="skill_afrika")
            serializer = FreelanceSerializer(
                freelancer,
                data={
                    "profile_pic_public_id": result["public_id"],
                    "profile_pic": result["secure_url"],
                },
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "File uploaded successfully",
                        "profile_pic": result["secure_url"],
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    operation_id="profile_picture_delete",
    summary="Delete Profile Picture",
    description=(
        "Allows authenticated users to delete an existing profile picture for a freelancer using their UUID. "
        "If no profile picture exists, the endpoint returns an appropriate error."
    ),
    responses={
        204: None,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Successful Deletion",
            value={},
            status_codes=["204"],
        ),
        OpenApiExample(
            "No Profile Picture",
            value={"error": "User has no profile picture"},
            status_codes=["400"],
        ),
        OpenApiExample(
            "Unauthorized User",
            value={"error": "User Unauthorized"},
            status_codes=["401"],
        ),
    ],
)
class ProfilePictureDeleteView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]

    def delete(self, request, uuid):
        try:
            freelancer = get_freelancer_profile_with_uuid(uuid)
            if request.user != freelancer.user:
                return Response(
                    {"error": "User Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
                )

            # Delete any file, if any
            if freelancer.profile_pic_public_id:
                delete_file_from_cloudinary(freelancer.profile_pic_public_id)
                freelancer.profile_pic_public_id = None
                freelancer.profile_pic = None

                freelancer.save()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": "User has no profile picture"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
