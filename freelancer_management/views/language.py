from django.db import transaction
from rest_framework import status, generics
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.filters import SearchFilter, OrderingFilter

from freelancer_management.views.profile import get_freelancer_profile_with_uuid
from freelancer_management.serializers import (
    FreelancerLanguageSerializer,
    FreelancerSkillSerializer,
    LanguageSerializer,
    SkillSerializer,
)
from freelancer_management.models import (
    FreelancerLanguage,
    FreelancerSkill,
    Language,
    Skill,
)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a list of all availabe languages",
        description="Retrieve a list of all languages that have been entered in the system.",
        responses={200: LanguageSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create a new language",
        description="Create a new language.",
        responses={201: LanguageSerializer},
    ),
)
class LanguageListCreateView(generics.ListCreateAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    ordering = ["name"]
    search_fields = ["name"]


class AddLanguageView(APIView):
    @extend_schema(
        summary="Add language to a freelancer",
        description="Add multiple languages to a freelancer's profile by passing a list of language IDs.",
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
                    "languages": {"type": "array", "items": {"type": "integer"}}
                },
                "required": ["languages"],
            }
        },
        responses={
            201: OpenApiResponse(
                response=FreelancerLanguageSerializer(many=True),
                description="Languages successfully added",
            ),
            400: OpenApiResponse(
                description="Bad Request - Invalid input or language not found"
            ),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                description="Example request to add language to a freelancer",
                value={"languages": [1, 2, 3]},
            ),
        ],
    )
    def post(self, request, uuid):
        freelancer = get_freelancer_profile_with_uuid(uuid)
        language_ids = request.data.get("languages", [])

        errors = []
        created_languages = []

        @transaction.atomic
        def create_freelancer_languages():
            for language_id in language_ids:
                try:
                    language = Language.objects.get(id=language_id)
                    freelancer_language, created = (
                        FreelancerLanguage.objects.get_or_create(
                            freelancer=freelancer, language=language
                        )
                    )
                    if created:
                        created_languages.append(freelancer_language.language.name)
                except Language.DoesNotExist:
                    errors.append(f"Language with id {language_id} does not exist.")
                except Exception as e:
                    errors.append(str(e))

        create_freelancer_languages()

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"added_languages": created_languages}, status=status.HTTP_201_CREATED
        )


class DeleteLanguageView(APIView):
    @extend_schema(
        summary="Delete a freelancer's language",
        description="Delete multiple languages from a freelancer's profile by passing a list of language IDs.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="UUID of the freelancer profile",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="languages",
                description="ID of languages to delete",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            204: OpenApiResponse(
                response={},
                description="languages successfully deleted",
            ),
            400: OpenApiResponse(
                description="Bad Request - Invalid input or language not found"
            ),
        },
    )
    def delete(self, request, uuid):
        freelancer = get_freelancer_profile_with_uuid(uuid)
        language_ids = request.GET.get("languages", "").split(",")

        errors = []

        @transaction.atomic
        def create_freelancer_language():
            for language_id in language_ids:
                try:
                    language = Language.objects.get(id=language_id)
                    freelancer_language = FreelancerLanguage.objects.get(
                        freelancer=freelancer, language=language
                    )
                    freelancer_language.delete()
                except Language.DoesNotExist:
                    errors.append(f"Language with id {language_id} does not exist.")
                except Exception as e:
                    errors.append(str(e))

        create_freelancer_language()

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_204_NO_CONTENT)
