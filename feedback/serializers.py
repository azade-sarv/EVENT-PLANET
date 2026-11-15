from rest_framework import serializers

from events.models import Event
from registrations.models import Registration
from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="registration.participant.username", read_only=True)
    event_title = serializers.CharField(source="registration.event.title", read_only=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "registration",
            "username",
            "event_title",
            "rating",
            "comment",
            "created_at",
        )
        read_only_fields = ("id", "registration", "username", "event_title", "created_at")

    def validate_registration(self, registration):
        user = self.context["request"].user
        
        if registration.participant != user:
            raise serializers.ValidationError(
                "You can only give feedback for your own registrations."
            )

        if registration.event.status != Event.Status.FINISHED:
            raise serializers.ValidationError(
                "Feedback can only be given for finished events."
            )

        return registration


class PublicFeedbackSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="registration.participant.username", read_only=True)

    class Meta:
        model = Feedback
        fields = ("id", "username", "rating", "comment", "created_at")