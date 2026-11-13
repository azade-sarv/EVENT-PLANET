from rest_framework import serializers

from events.models import Event
from .models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    event_start_time = serializers.DateTimeField(
        source="event.start_time", read_only=True
    )

    class Meta:
        model = Registration
        fields = (
            "id",
            "event",
            "event_title",
            "event_start_time",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")

    def validate_event(self, event):
        if event.status != Event.Status.PUBLISHED:
            raise serializers.ValidationError(
                "Only published events can be registered."
            )

        if event.available_spots <= 0:
            raise serializers.ValidationError("This event is full.")

        return event

    def validate(self, attrs):
        event = attrs.get("event")
        user = self.context["request"].user

        if Registration.objects.filter(
            event=event, participant=user
        ).exists():
            raise serializers.ValidationError(
                "You are already registered for this event."
            )

        return attrs


class MyRegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    event_start_time = serializers.DateTimeField(
        source="event.start_time", read_only=True
    )
    has_feedback = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = (
            "id",
            "event",
            "event_title",
            "event_start_time",
            "status",
            "has_feedback",
            "created_at",
        )

    def get_has_feedback(self, obj):
        return hasattr(obj, "feedback")


class ParticipantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="participant.username", read_only=True)
    email = serializers.CharField(source="participant.email", read_only=True)

    class Meta:
        model = Registration
        fields = ("id", "participant", "username", "email", "status", "created_at")