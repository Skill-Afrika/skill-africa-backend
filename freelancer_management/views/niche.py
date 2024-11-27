from django.db import transaction
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.filters import SearchFilter, OrderingFilter

from freelancer_management.views.profile import get_freelancer_profile_with_uuid
from skill_africa.permissions import IsAdmin
from freelancer_management.serializers import (
    FreelanceProfileSerializer,
    NicheSerializer,
)
from freelancer_management.models import FreelancerNiche, Niche


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


class AddNicheView(APIView):
    @extend_schema(
        summary="Add niche to a freelancer",
        description="Add multiple niche to a freelancer's profile by passing a list of niche IDs.",
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
                    "niches": {"type": "array", "items": {"type": "integer"}}
                },
                "required": ["niches"],
            }
        },
        responses={
            201: OpenApiResponse(
                response={},
                description="Niches successfully added",
            ),
            400: OpenApiResponse(
                description="Bad Request - Invalid input or niche not found"
            ),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                description="Example request to add niches to a freelancer",
                value={"niches": [1, 2, 3]},
            ),
            OpenApiExample(
                "Response Example",
                description="Example response after successfully adding niches",
            ),
        ],
    )
    def post(self, request, uuid):
        freelancer = get_freelancer_profile_with_uuid(uuid)
        niche_ids = request.data.get("niches", [])

        # To make sure the user does not add more than 3 niches
        niche_id_number = len(niche_ids)
        niche_number = len(
            FreelanceProfileSerializer(instance=freelancer).data["niches"]
        )
        total_niches = niche_id_number + niche_number
        if total_niches > 3:
            return Response(
                {"error": "Maximum of 3 Niches Per user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        errors = []
        created_niches = []

        @transaction.atomic
        def create_freelancer_niche():
            for niche_id in niche_ids:
                try:
                    niche = Niche.objects.get(id=niche_id)
                    freelancer_niche, created = FreelancerNiche.objects.get_or_create(
                        freelancer=freelancer, niche=niche
                    )
                    if created:
                        created_niches.append(freelancer_niche.niche.name)
                except Niche.DoesNotExist:
                    errors.append(f"Niche with id {niche_id} does not exist.")
                except Exception as e:
                    errors.append(str(e))

        create_freelancer_niche()

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"created_niches": created_niches}, status=status.HTTP_201_CREATED
        )


class DeleteNicheView(APIView):
    @extend_schema(
        summary="Delete a freelancer's niche",
        description="Delete multiple niches from a freelancer's profile by passing a list of niche IDs.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="UUID of the freelancer profile",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="niches",
                description="ID of niches to delete",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "niches": {"type": "array", "items": {"type": "integer"}}
                },
                "required": ["niches"],
            }
        },
        responses={
            204: OpenApiResponse(
                response={},
                description="Niches successfully deleted",
            ),
            400: OpenApiResponse(
                description="Bad Request - Invalid input or niche not found"
            ),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                description="Example request to delete niches from a freelancer",
                value={"niches": [1, 2, 3]},
            ),
        ],
    )
    def delete(self, request, uuid):
        freelancer = get_freelancer_profile_with_uuid(uuid)
        niche_ids = request.GET.get("niches", "").split(",")

        errors = []

        @transaction.atomic
        def create_freelancer_niche():
            for niche_id in niche_ids:
                try:
                    niche = Niche.objects.get(id=niche_id)
                    freelancer_niche = FreelancerNiche.objects.get(
                        freelancer=freelancer, niche=niche
                    )
                    freelancer_niche.delete()
                except Niche.DoesNotExist:
                    errors.append(f"Niche with id {niche_id} does not exist.")
                except Exception as e:
                    errors.append(str(e))

        create_freelancer_niche()

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_204_NO_CONTENT)
