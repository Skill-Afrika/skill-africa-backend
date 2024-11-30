from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.filters import SearchFilter, OrderingFilter

from freelancer_management.models import WorkExperience
from freelancer_management.serializers import (
    FreelanceSerializer,
    WorkExperienceSerializer,
)
from freelancer_management.views.profile import get_freelancer_profile_with_uuid
from skill_africa.permissions import IsAuthenticatedWithJWT
from skill_africa.utils import delete_file_from_cloudinary, upload_file_to_cloudinary


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a list of freelancer's Work Experience",
        description="Retrieve a list of freelancer's Work Experiences.",
        responses={200: WorkExperienceSerializer(many=True)},
    ),
)
class WorkExperienceListView(generics.ListAPIView):
    serializer_class = WorkExperienceSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    ordering = ["start_date", "end_date", "job_title", "company", "description"]
    search_fields = ["job_title", "company", "description"]

    def get_queryset(self):
        uuid = self.kwargs.get("uuid")
        freelancer = get_freelancer_profile_with_uuid(uuid)
        return WorkExperience.objects.filter(freelancer=freelancer)


class WorkExperienceCreateView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]

    @extend_schema(
        summary="Add a new work experience",
        description="Endpoints for freelancers to add new work experience in their profile.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="UUID of the freelancer profile",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "job_title": {"type": "string"},
                    "company": {"type": "string"},
                    "company_url": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "description": {"type": "string"},
                    "current_role": {"type": "boolean"},
                },
                "required": ["job_title", "company", "start_date", "description"],
            }
        },
        responses={
            201: OpenApiResponse(
                response=WorkExperienceSerializer,
                description="Work Experience successfully created",
            ),
            400: OpenApiResponse(description="Bad Request - Invalid input"),
            401: OpenApiResponse(description="Not Authorized"),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                description="Example request to add a new work experience for a freelancer",
                value={
                    "job_title": "Full Stack Developer",
                    "company": "Google",
                    "company_url": "https://google.com",
                    "start_date": "2022-12-22",
                    "end_date": "2023-12-23",
                    "description": "really cool place to work",
                    "current_role": False,
                },
            ),
        ],
    )
    def post(self, request, uuid):
        freelancer = get_freelancer_profile_with_uuid(uuid)

        # Only the profile owner can add a work experience
        if request.user != freelancer.user:
            return Response(
                {"error": "User is unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = WorkExperienceSerializer(
            data={**request.data, "freelancer": freelancer.id}
        )
        if serializer.is_valid():
            workExperience = serializer.save()
            return Response(
                WorkExperienceSerializer(workExperience).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkExperienceDeleteView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]

    @extend_schema(
        summary="Delete an experience",
        description="Endpoints for freelancers to Delete an experience in their profile.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="UUID of the freelancer profile",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="id",
                description="The Work Experience ID",
                required=True,
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            204: OpenApiResponse(
                response={},
                description="Work Experience successfully deleted",
            ),
            400: OpenApiResponse(description="Bad Request - Invalid input"),
            401: OpenApiResponse(description="Not Authorized"),
        },
    )
    def delete(self, request, uuid, id):
        freelancer = get_freelancer_profile_with_uuid(uuid)

        # Only the profile owner can create a project
        if request.user != freelancer.user:
            return Response(
                {"error": "User is unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        workExperience = get_object_or_404(WorkExperience, id=id)
        workExperience.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    operation_id="resume_upload",
    summary="Upload Resume",
    description=(
        "Allows authenticated users to upload a resume for a freelancer using their UUID. "
        "The file must be a pdf and will replace any existing resume. Size must be less than 5mb"
    ),
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "resume": {
                    "type": "string",
                    "format": "binary",
                    "description": "Pdf file to be uploaded.",
                }
            },
            "required": ["resume"],
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
                "resume": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
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
class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]
    SUPPORTED_MIME_TYPES = ["application/pdf"]
    MAX_FILE_SIZE_MB = 5

    def post(self, request, uuid):
        try:
            file = request.FILES.get("resume")
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
            if freelancer.resume_public_id:
                delete_file_from_cloudinary(freelancer.resume_public_id)

            # Upload the file to Cloudinary
            result = upload_file_to_cloudinary(file, folder="skill_afrika")
            serializer = FreelanceSerializer(
                freelancer,
                data={
                    "resume_public_id": result["public_id"],
                    "resume": result["secure_url"],
                },
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "File uploaded successfully",
                        "resume": result["secure_url"],
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
    operation_id="resume_delete",
    summary="Delete Resume",
    description=(
        "Allows authenticated users to delete an existing resume for a freelancer using their UUID. "
        "If no resume exists, the endpoint returns an appropriate error."
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
            "No Resume",
            value={"error": "User has no resume"},
            status_codes=["400"],
        ),
        OpenApiExample(
            "Unauthorized User",
            value={"error": "User Unauthorized"},
            status_codes=["401"],
        ),
    ],
)
class ResumeDeleteView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]

    def delete(self, request, uuid):
        try:
            freelancer = get_freelancer_profile_with_uuid(uuid)
            if request.user != freelancer.user:
                return Response(
                    {"error": "User Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
                )

            # Delete any file, if any
            if freelancer.resume_public_id:
                delete_file_from_cloudinary(freelancer.resume_public_id)
                freelancer.resume_public_id = None
                freelancer.resume = None

                freelancer.save()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": "User has no resume"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
