from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response

from freelancer_management.views.profile import get_freelancer_profile_with_uuid
from skill_africa.permissions import IsProfileOwner
from freelancer_management.serializers import FreelancerLinkSerializer
from freelancer_management.models import FreelancerLink


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
