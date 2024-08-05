from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from profile_management.serializers import DocumentationRegisterSerializer
from profile_management.views import registerUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.filters import SearchFilter, OrderingFilter

from skill_africa.permissions import IsAdmin, IsAuthenticatedWithJWT, IsProfileOwner
from .serializers import (
    FreelanceSerializer,
    FreelanceProfileSerializer,
    FreelancerSkillSerializer,
    FreelancerLinkSerializer,
    NicheSerializer,
    SkillSerializer,
)
from .models import FreelancerLink, FreelancerProfile, FreelancerSkill, Niche, Skill
from .filters import CustomOrderingFilter, CustomSearchFilter


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


@extend_schema_view(
    post=extend_schema(
        summary="Add a new link to a user's profile",
        description="Add a new link to a user's profile.",
        request=FreelancerLinkSerializer,
        responses={201: FreelancerLinkSerializer},
    )
)
class FreelancerLinkListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsProfileOwner]

    def get_object(self, uuid):
        return get_freelancer_profile_with_uuid(uuid)

    def post(self, request, uuid):
        profile = self.get_object(uuid)
        self.check_object_permissions(request, profile)
        serializer = FreelancerLinkSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(freelancer=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    put=extend_schema(
        summary="Update an existing link on a user's profile",
        description="Update an existing link on a user's profile.",
        request=FreelancerLinkSerializer,
        responses={200: FreelancerLinkSerializer},
    ),
    delete=extend_schema(
        summary="Delete a link from a user's profile",
        description="Delete a link from a user's profile.",
        responses={204: None},
    ),
)
class FreelancerLinkDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsProfileOwner]

    def get_object(self, uuid):
        return get_freelancer_profile_with_uuid(uuid)

    def put(self, request, uuid, linkId):
        profile = self.get_object(uuid)
        self.check_object_permissions(request, profile)
        link = get_object_or_404(FreelancerLink, id=linkId, freelancer=profile)
        serializer = FreelancerLinkSerializer(link, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid, linkId):
        profile = self.get_object(uuid)
        self.check_object_permissions(request, profile)
        link = get_object_or_404(FreelancerLink, id=linkId, freelancer=profile)
        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a list of all available niches",
        description="Retrieve a list of all available niches.",
        responses={200: NicheSerializer(many=True)},
    ),
)
class NicheListView(generics.ListAPIView):
    queryset = Niche.objects.all()
    serializer_class = NicheSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    ordering = ["name"]
    search_fields = ["name"]


@extend_schema_view(
    post=extend_schema(
        summary="Create a new niche",
        description="Create a new niche.",
        responses={201: NicheSerializer},
    ),
)
class NicheCreateView(generics.CreateAPIView):
    queryset = Niche.objects.all()
    serializer_class = NicheSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]


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
                        created_skills.append(freelancer_skill)
                except Skill.DoesNotExist:
                    errors.append(f"Skill with id {skill_id} does not exist.")
                except Exception as e:
                    errors.append(str(e))

        create_freelancer_skills()

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FreelancerSkillSerializer(created_skills, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
