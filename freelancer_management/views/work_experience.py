from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.filters import SearchFilter, OrderingFilter

from freelancer_management.models import WorkExperience
from freelancer_management.serializers import WorkExperienceSerializer
from freelancer_management.views.profile import get_freelancer_profile_with_uuid
from skill_africa.permissions import IsAuthenticatedWithJWT


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
