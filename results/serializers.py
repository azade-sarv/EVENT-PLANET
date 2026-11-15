from rest_framework import serializers

from events.models import Event
from .models import EventResult, ResultEntry


class ResultEntrySerializer(serializers.ModelSerializer):
    participant_username = serializers.CharField(
        source="participant.username", read_only=True
    )

    class Meta:
        model = ResultEntry
        fields = (
            "id",
            "result",
            "participant",
            "participant_username",
            "entry_type",
            "rank",
            "score",
        )
        read_only_fields = ("id", "participant_username")


class EventResultSerializer(serializers.ModelSerializer):
    entries = ResultEntrySerializer(many=True, read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = EventResult
        fields = (
            "id",
            "event",
            "event_title",
            "summary",
            "is_published",
            "published_at",
            "entries",
            "created_at",
        )
        read_only_fields = ("id", "published_at", "entries")

    def validate_event(self, event):
        user = self.context["request"].user
        if event.organizer != user:
            raise serializers.ValidationError(
                "You can only manage results for your own events."
            )
        return event

    def validate_is_published(self, value):
        if value is True:
            event = self.instance.event if self.instance else self.initial_data.get("event")
            if isinstance(event, int):
                event = Event.objects.get(pk=event)
            
            if event.status != Event.Status.FINISHED:
                raise serializers.ValidationError(
                    "Results can only be published for finished events."
                )
        return value


class PublicEventResultSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    entries = ResultEntrySerializer(many=True, read_only=True)

    class Meta:
        model = EventResult
        fields = (
            "id",
            "event_title",
            "summary",
            "published_at",
            "entries",
        )