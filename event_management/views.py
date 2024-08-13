from rest_framework import generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework_simplejwt.authentication import JWTAuthentication

from admin_management.models import AdminProfile
from admin_management.serializers import AdminSerializer
from profile_management.models import User
from profile_management.serializers import UserDetailsSerializerWithId
from skill_africa.permissions import IsAdmin, IsAuthenticatedWithJWT
from .models import Event, EventAttendee, EventCoHost
from .serializers import (
    CreateEventSerializer,
    EventAttendeeListSerializer,
    EventSerializer,
    EventAttendeeSerializer,
    EventCoHostSerializer,
)
from .filters import CustomOrderingFilter, CustomSearchFilter


# Event Views
@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a list of all events",
        description="Retrieve a list of all events.",
        responses={200: EventSerializer(many=True)},
    ),
)
class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [CustomSearchFilter, CustomOrderingFilter]
    ordering_fields = ["name", "datetime", "location"]
    ordering = ["datetime"]
    search_fields = [
        "name",
        "location",
        "datetime",
        "details",
        "host__first_name",
        "host__last_name",
    ]


class EventCreateView(APIView):
    serializer_class = CreateEventSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedWithJWT]

    @extend_schema(
        summary="Create a new event",
        description="Create a new event.",
        request=CreateEventSerializer,
        responses={
            201: EventSerializer,
            400: OpenApiResponse(description="Invalid data"),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve detailed information for a specific event",
        description="Retrieve detailed information for a specific event.",
        responses={200: EventSerializer},
        parameters=[
            OpenApiParameter(
                "uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="UUID of the event",
            )
        ],
    ),
    put=extend_schema(
        summary="Update an existing event",
        description="Update an existing event.",
        request=CreateEventSerializer,
        responses={200: EventSerializer},
        parameters=[
            OpenApiParameter(
                "uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="UUID of the event",
            )
        ],
    ),
    delete=extend_schema(
        summary="Delete a specific event",
        description="Delete a specific event.",
        responses={204: OpenApiResponse(description="No Content")},
        parameters=[
            OpenApiParameter(
                "uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="UUID of the event",
            )
        ],
    ),
)
class EventDetailView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]
    authentication_classes = [JWTAuthentication]

    def get(self, request, uuid):
        event = get_object_or_404(Event, uuid=uuid)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def put(self, request, uuid):
        event = get_object_or_404(Event, uuid=uuid)
        serializer = CreateEventSerializer(event, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):
        event = get_object_or_404(Event, uuid=uuid)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Event Attendees Views
@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a list of all event's Attendees",
        description="Retrieve a list of all event's Attendees.",
        request=EventAttendeeListSerializer,
        responses={200: EventAttendeeListSerializer(many=True)},
    ),
)
class EventAttendeeListView(generics.ListAPIView):
    serializer_class = EventAttendeeListSerializer
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    ordering = ["attendee__username"]
    search_fields = [
        "attendee__username",
        "attendee__email",
    ]

    def get_queryset(self):
        event_uuid = self.kwargs.get("event_uuid")
        return EventAttendee.objects.filter(event__uuid=event_uuid)


@extend_schema_view(
    post=extend_schema(
        summary="Register to attend a specific event",
        description="Register the currently signed in user to attend a specific event.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "event": {"type": "string", "format": "uuid"},
                },
                "required": ["event"],
                "example": {
                    "event": "123e4567-e89b-12d3-a456-426614174000",
                },
            }
        },
        responses={201: EventAttendeeSerializer},
    ),
)
class EventAttendeeCreateView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        attendee = UserDetailsSerializerWithId(request.user).data
        attendee_data = {"event": request.data["event"], "attendee": attendee["id"]}
        serializer = EventAttendeeSerializer(data=attendee_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    delete=extend_schema(
        summary="Unregister from a specific event",
        description="Unregister from a specific event.",
        responses={204: OpenApiResponse(description="No Content")},
        parameters=[
            OpenApiParameter(
                "uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="UUID of the event",
            ),
            OpenApiParameter(
                "attendeeId",
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                description="ID of the attendee",
            ),
        ],
    )
)
class EventAttendeeDeleteView(APIView):
    permission_classes = [IsAuthenticatedWithJWT]
    authentication_classes = [JWTAuthentication]

    def delete(self, request, uuid, attendeeUuid):
        event = get_object_or_404(Event, uuid=uuid)
        attendee = get_object_or_404(User, uuid=attendeeUuid)

        if request.user != attendee and not request.user["role"] == "admin":
            return Response(status=status.HTTP_403_FORBIDDEN)

        event_attendee = get_object_or_404(
            EventAttendee, event=event, attendee=attendee
        )
        event_attendee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Event CoHosts Views
@extend_schema_view(
    post=extend_schema(
        summary="Add a co-host to a specific event",
        description="Add a co-host to a specific event.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "cohost": {"type": "string", "format": "uuid"},
                    "event": {"type": "string", "format": "uuid"},
                },
                "required": ["cohost", "event"],
                "example": {
                    "cohost": "123e4567-e89b-12d3-a456-426614174000",
                    "event": "123e4567-e89b-12d3-a456-426614174000",
                },
            }
        },
        responses={201: EventCoHostSerializer},
    )
)
class EventCoHostCreateView(APIView):
    permission_classes = [IsAdmin]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        cohost_uuid = request.data.get("cohost")
        cohost_object = get_object_or_404(User, uuid=cohost_uuid)
        cohost = UserDetailsSerializerWithId(cohost_object).data
        cohost_data = {"event": request.data["event"], "cohost": cohost["id"]}
        serializer = EventCoHostSerializer(data=cohost_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    delete=extend_schema(
        summary="Remove a co-host from a specific event",
        description="Remove a co-host from a specific event.",
        responses={204: OpenApiResponse(description="No Content")},
        parameters=[
            OpenApiParameter(
                "uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="UUID of the event",
            ),
            OpenApiParameter(
                "cohostUuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="UUID of the co-host",
            ),
        ],
    )
)
class EventCoHostDeleteView(APIView):
    permission_classes = [IsAdmin]
    authentication_classes = [JWTAuthentication]

    def delete(self, request, uuid, cohostUuid):
        event = get_object_or_404(Event, uuid=uuid)
        cohost = get_object_or_404(User, uuid=cohostUuid)
        event_cohost = get_object_or_404(EventCoHost, event=event, cohost=cohost)
        event_cohost.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
