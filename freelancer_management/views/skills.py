from django.db import transaction
from rest_framework import status, generics
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.filters import SearchFilter, OrderingFilter

from freelancer_management.views.profile import get_freelancer_profile_with_uuid
from freelancer_management.serializers import FreelancerSkillSerializer, SkillSerializer
from freelancer_management.models import FreelancerSkill, Skill


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a list of all available skills",
        description="Retrieve a list of all available skills.",
        responses={200: SkillSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create a new skill",
        description="Create a new skill.",
        responses={201: SkillSerializer},
    ),
)
class SkillListCreateView(generics.ListCreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    ordering = ["name"]
    search_fields = ["name"]


class AddSkillsView(APIView):
    @extend_schema(
        summary="Add skills to a freelancer",
        description="Add multiple skills to a freelancer's profile by passing a list of skill IDs.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="UUID of the freelancer profile",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "skills": {"type": "array", "items": {"type": "integer"}}
                },
                "required": ["skills"],
            }
        },
        responses={
            201: OpenApiResponse(
                response=FreelancerSkillSerializer(many=True),
                description="Skills successfully added",
            ),
            400: OpenApiResponse(
                description="Bad Request - Invalid input or skills not found"
            ),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                description="Example request to add skills to a freelancer",
                value={"skills": [1, 2, 3]},
            ),
            OpenApiExample(
                "Response Example",
                description="Example response after successfully adding skills",
                value=[
                    {"id": 1, "freelancer": 1, "skill": 1},
                    {"id": 2, "freelancer": 1, "skill": 2},
                    {"id": 3, "freelancer": 1, "skill": 3},
                ],
            ),
        ],
    )
    def post(self, request, uuid):
        freelancer = get_freelancer_profile_with_uuid(uuid)
        skill_ids = request.data.get("skills", [])

        errors = []
        created_skills = []

        @transaction.atomic
        def create_freelancer_skills():
            for skill_id in skill_ids:
                try:
                    skill = Skill.objects.get(id=skill_id)
                    freelancer_skill, created = FreelancerSkill.objects.get_or_create(
                        freelancer=freelancer, skill=skill
                    )
                    if created:
                        created_skills.append(freelancer_skill.skill.name)
                except Skill.DoesNotExist:
                    errors.append(f"Skill with id {skill_id} does not exist.")
                except Exception as e:
                    errors.append(str(e))

        create_freelancer_skills()

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"created_skills": created_skills}, status=status.HTTP_201_CREATED
        )


class DeleteSkillView(APIView):
    @extend_schema(
        summary="Delete a freelancer's skills",
        description="Delete multiple skills from a freelancer's profile by passing a list of skill IDs.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="UUID of the freelancer profile",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="skills",
                description="ID of skills to delete",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "skills": {"type": "array", "items": {"type": "integer"}}
                },
                "required": ["skills"],
            }
        },
        responses={
            204: OpenApiResponse(
                response={},
                description="Skills successfully deleted",
            ),
            400: OpenApiResponse(
                description="Bad Request - Invalid input or niche not found"
            ),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                description="Example request to delete skills from a freelancer",
                value={"skills": [1, 2, 3]},
            ),
        ],
    )
    def delete(self, request, uuid):
        freelancer = get_freelancer_profile_with_uuid(uuid)
        skill_ids = request.GET.get("skills", "").split(",")

        errors = []

        @transaction.atomic
        def create_freelancer_skill():
            for skill_id in skill_ids:
                try:
                    skill = Skill.objects.get(id=skill_id)
                    freelancer_skill = FreelancerSkill.objects.get(
                        freelancer=freelancer, skill=skill
                    )
                    freelancer_skill.delete()
                except Skill.DoesNotExist:
                    errors.append(f"Skill with id {skill_id} does not exist.")
                except Exception as e:
                    errors.append(str(e))

        create_freelancer_skill()

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_204_NO_CONTENT)
