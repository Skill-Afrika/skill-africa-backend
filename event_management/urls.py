from django.urls import path
from .views import (
    EventAttendeeCreateView,
    EventAttendeeListView,
    EventListView,
    EventAttendeeDeleteView,
    EventCoHostCreateView,
    EventCoHostDeleteView,
    EventCreateView,
    EventDetailView,
)

urlpatterns = [
    path("create-event", EventCreateView.as_view(), name="event-create"),
    path("events-list", EventListView.as_view(), name="event-list"),
    path("<str:uuid>", EventDetailView.as_view(), name="event-detail"),
    path(
        "<str:event_uuid>/attendees",
        EventAttendeeListView.as_view(),
        name="event-attendee-list",
    ),
    path(
        "attendees/",
        EventAttendeeCreateView.as_view(),
        name="event-attendee-create",
    ),
    path(
        "<str:uuid>/attendees/<str:attendeeUuid>",
        EventAttendeeDeleteView.as_view(),
        name="event-attendee-delete",
    ),
    path(
        "cohosts/",
        EventCoHostCreateView.as_view(),
        name="event-cohost-create",
    ),
    path(
        "<str:uuid>/cohosts/<str:cohostUuid>",
        EventCoHostDeleteView.as_view(),
        name="event-cohost-delete",
    ),
]
