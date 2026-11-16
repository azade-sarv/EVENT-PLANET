from rest_framework import serializers

from events.models import Event
from registrations.models import Registration

from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="registration.participant.username", read_only=True
    )
    event_title = serializers.CharField(
        source="registration.event.title", read_only=True
    )
    event = serializers.IntegerField(source="registration.event_id", read_only=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "registration",
            "event",
            "username",
            "event_title",
            "rating",
            "comment",
            "created_at",
        )
        read_only_fields = ("id", "username", "event_title", "created_at")
        extra_kwargs = {
            "registration": {
                "error_messages": {
                    "unique": "Feedback already submitted for this registration."
                }
            }
        }

    def validate_registration(self, registration):
        user = self.context["request"].user

        if registration.participant_id != user.id:
            raise serializers.ValidationError(
                "You can only give feedback for your own registrations."
            )

        if registration.status != Registration.Status.CONFIRMED:
            raise serializers.ValidationError(
                "Your registration for this event is cancelled."
            )

        if registration.event.status != Event.Status.FINISHED:
            raise serializers.ValidationError(
                "Feedback can only be given for finished events."
            )

        if self.instance is not None and registration != self.instance.registration:
            raise serializers.ValidationError(
                "Registration cannot be changed. Create a new feedback instead."
            )

        return registration


class OrganizerFeedbackSerializer(serializers.ModelSerializer):
    participant_id = serializers.IntegerField(
        source="registration.participant_id", read_only=True
    )
    username = serializers.CharField(
        source="registration.participant.username", read_only=True
    )

    class Meta:
        model = Feedback
        fields = ("id", "participant_id", "username", "rating", "comment", "created_at")


class PublicFeedbackSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="registration.participant.username", read_only=True
    )

    class Meta:
        model = Feedback
        fields = ("id", "username", "rating", "comment", "created_at")