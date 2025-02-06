from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.filters import SearchFilter, OrderingFilter

from freelancer_management.models import Project
from freelancer_management.serializers import FreelanceSerializer, ProjectSerializer
from freelancer_management.views.profile import get_freelancer_profile_with_uuid
from skill_africa.permissions import IsAuthenticatedWithJWT
from skill_africa.utils import delete_file_from_cloudinary, upload_file_to_cloudinary


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a list of freelancer's projects",
        description="Retrieve a list of freelancer's projects.",
        responses={200: ProjectSerializer(many=True)},
    ),
)
class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    ordering = ["name"]
    search_fields = ["name"]

    def get_queryset(self):
        uuid = self.kwargs.get("uuid")
        freelancer = get_freelancer_profile_with_uuid(uuid)
        return Project.objects.filter(freelancer=freelancer)


class ProjectCreateView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]

    @extend_schema(
        summary="Create a new Project",
        description="Endpoints for freelancers to Create a new Project in their profile.",
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
                    "name": {"type": "string"},
                    "url": {"type": "string"},
                    "skills": {"type": "string"},
                    "tools": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["name", "url"],
            }
        },
        responses={
            201: OpenApiResponse(
                response=ProjectSerializer,
                description="Project successfully created",
            ),
            400: OpenApiResponse(description="Bad Request - Invalid input"),
            401: OpenApiResponse(description="Not Authorized"),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                description="Example request to create a project for a freelancer",
                value={
                    "name": "Learn 3 Play",
                    "url": "https://learn3play.simondevz.xyz",
                    "skills": "A comma seperated list of skills used e.g backend development, frontend development, designing",
                    "tools": "A comma seperated list of tools used e.g figma, react, nodeJs",
                    "description": "Description of the project (Best to send in markdown format)",
                },
            ),
        ],
    )
    def post(self, request, uuid):
        name = request.data.get("name", "")
        url = request.data.get("url", "")
        skills = request.data.get("skills", "")
        tools = request.data.get("tools", "")
        description = request.data.get("description", "")
        freelancer = get_freelancer_profile_with_uuid(uuid)

        # Only the profile owner can create a project
        if request.user != freelancer.user:
            return Response(
                {"error": "User is unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = ProjectSerializer(
            data={
                "name": name,
                "url": url,
                "freelancer": freelancer.id,
                "skills": skills,
                "tools": tools,
                "description": description,
            }
        )
        if serializer.is_valid():
            project = serializer.save()
            return Response(
                ProjectSerializer(project).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDeleteView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]

    @extend_schema(
        summary="Delete a Project",
        description="Endpoints for freelancers to Delete a Project in their profile.",
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
                description="The project ID",
                required=True,
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            204: OpenApiResponse(
                response={},
                description="Project successfully deleted",
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

        project = get_object_or_404(Project, id=id)
        project.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    operation_id="project_cover_image_upload",
    summary="Upload Cover Image for Project",
    description=(
        "Allows authenticated users to upload a cover image for their project using the project ID. "
        "The file must be an image (JPEG or PNG) and will replace any existing cover image."
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
                "cover_image": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
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
class CoverImageUploadView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]
    SUPPORTED_MIME_TYPES = ["image/jpeg", "image/png"]
    MAX_FILE_SIZE_MB = 5

    def post(self, request, uuid, id):
        try:
            file = request.FILES.get("image")
            freelancer = get_freelancer_profile_with_uuid(uuid)
            project = get_object_or_404(Project, id=id)

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
            if project.image_public_id:
                delete_file_from_cloudinary(project.image_public_id)

            # Upload the file to Cloudinary
            result = upload_file_to_cloudinary(file, folder="skill_afrika")
            serializer = ProjectSerializer(
                project,
                data={
                    "image_public_id": result["public_id"],
                    "image": result["secure_url"],
                },
                partial=True,
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "File uploaded successfully",
                        "cover_image": result["secure_url"],
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
    operation_id="project_cover_image_delete",
    summary="Delete Project Cover Image",
    description=(
        "Allows authenticated users to delete an existing cover image for an existing project using its ID. "
        "If no cover image exists, the endpoint returns an appropriate error."
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
            "No Cover Image",
            value={"error": "Project has no cover image"},
            status_codes=["400"],
        ),
        OpenApiExample(
            "Unauthorized User",
            value={"error": "User Unauthorized"},
            status_codes=["401"],
        ),
    ],
)
class CoverImageDeleteView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]

    def delete(self, request, uuid, id):
        try:
            freelancer = get_freelancer_profile_with_uuid(uuid)
            project = get_object_or_404(Project, id=id)
            if request.user != freelancer.user:
                return Response(
                    {"error": "User Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
                )

            # Delete any file, if any
            if project.image_public_id:
                delete_file_from_cloudinary(project.image_public_id)
                project.image = None
                project.image_public_id = None

                project.save()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": "Project has no cover image"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
