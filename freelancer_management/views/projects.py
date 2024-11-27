from rest_framework import generics, status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.filters import SearchFilter, OrderingFilter

from freelancer_management.serializers import ProjectSerializer
from freelancer_management.views.profile import get_freelancer_profile_with_uuid
from skill_africa.permissions import IsAuthenticatedWithJWT, IsProfileOwner


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
                "properties": {"name": {"type": "string"}, "url": {"type": "string"}},
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
                },
            ),
        ],
    )
    def post(self, request, uuid):
        name = request.data.get("name", "")
        url = request.data.get("url", "")
        freelancer = get_freelancer_profile_with_uuid(uuid)

        # Only the profile owner can create a project
        if request.user != freelancer.user:
            return Response(
                {"error": "User is unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = ProjectSerializer(
            data={"name": name, "url": url, "freelancer": freelancer.id}
        )
        if serializer.is_valid():
            project = serializer.save()
            return Response(
                ProjectSerializer(project).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
