from rest_framework import serializers
from admin_management.serializers import AdminProfileSerializer
from profile_management.serializers import UserDetailsSerializer
from .models import Event, EventAttendee, EventCoHost


class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    host = AdminProfileSerializer()

    class Meta:
        model = Event
        depth = 1
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["cohosts"] = EventAttendeeListSerializer(
            instance.cohosts, many=True
        ).data
        representation["attendees"] = len(
            EventAttendeeListSerializer(instance.attendees, many=True).data
        )
        return representation


class EventAttendeeListSerializer(serializers.ModelSerializer):
    attendee = UserDetailsSerializer(read_only=True)

    class Meta:
        model = EventAttendee
        fields = "__all__"


class EventAttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAttendee
        fields = "__all__"


class EventCoHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCoHost
        fields = "__all__"
