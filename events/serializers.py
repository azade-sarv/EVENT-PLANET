from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    organizer_username = serializers.CharField(
        source="organizer.username", read_only=True
    )
    confirmed_count = serializers.IntegerField(read_only=True)
    available_spots = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "start_time",
            "end_time",
            "capacity",
            "status",
            "organizer_username",
            "confirmed_count",
            "available_spots",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate(self, attrs):
        start = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end = attrs.get("end_time", getattr(self.instance, "end_time", None))

        if start and end and start >= end:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time."}
            )

        if self.instance is not None:
            if self.instance.status == Event.Status.FINISHED:
                raise serializers.ValidationError(
                    "Finished events cannot be modified."
                )

            capacity = attrs.get("capacity", self.instance.capacity)
            confirmed = self.instance.confirmed_count
            if capacity < confirmed:
                raise serializers.ValidationError(
                    {"capacity": f"Capacity cannot be less than {confirmed} confirmed registrations."}
                )

        return attrs


class PublicEventSerializer(serializers.ModelSerializer):
    organizer_username = serializers.CharField(
        source="organizer.username", read_only=True
    )
    available_spots = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    feedback_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "start_time",
            "end_time",
            "capacity",
            "available_spots",
            "average_rating",
            "feedback_count",
            "organizer_username",
        )


class EventStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("status",)

    def validate_status(self, value):
        current = self.instance.status

        if value == current:
            raise serializers.ValidationError(
                f"Event is already in '{current}' status."
            )

        allowed = Event.ALLOWED_TRANSITIONS[current]
        if value not in allowed:
            allowed_text = ", ".join(allowed) if allowed else "none"
            raise serializers.ValidationError(
                f"Cannot transition from '{current}' to '{value}'. Allowed: {allowed_text}."
            )

        return value