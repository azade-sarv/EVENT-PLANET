from rest_framework import serializers

from events.models import Event
from registrations.models import Registration

from .models import EventResult, ResultEntry


class ResultEntrySerializer(serializers.ModelSerializer):
    participant_username = serializers.SerializerMethodField()
    entry_type = serializers.ChoiceField(choices=ResultEntry.EntryType.choices)
    label = serializers.CharField(max_length=200, required=False, allow_blank=True)

    class Meta:
        model = ResultEntry
        fields = (
            "id",
            "result",
            "entry_type",
            "participant",
            "participant_username",
            "label",
            "rank",
            "score",
            "notes",
        )
        read_only_fields = ("id", "participant_username")

    def get_participant_username(self, obj):
        return obj.participant.username if obj.participant_id else None

    def validate(self, attrs):
        user = self.context["request"].user

        result = attrs.get("result") or getattr(self.instance, "result", None)
        if result is None:
            raise serializers.ValidationError({"result": "This field is required."})

        if result.event.organizer != user:
            raise serializers.ValidationError(
                {"result": "You can only manage entries for your own events."}
            )

        if result.is_published:
            raise serializers.ValidationError(
                {"result": "Published results cannot be modified. Unpublish first."}
            )

        entry_type = attrs.get(
            "entry_type", getattr(self.instance, "entry_type", None)
        )
        if entry_type is None:
            raise serializers.ValidationError(
                {"entry_type": "This field is required."}
            )

        participant = attrs.get(
            "participant", getattr(self.instance, "participant", None)
        )
        rank = attrs.get("rank", getattr(self.instance, "rank", None))
        label = attrs.get("label", getattr(self.instance, "label", ""))

        if entry_type == ResultEntry.EntryType.RANKING:
            if result.event.event_type != Event.EventType.TOURNAMENT:
                raise serializers.ValidationError(
                    {"entry_type": "Ranking results are only allowed for tournaments."}
                )

            if rank is None:
                raise serializers.ValidationError(
                    {"rank": "Ranking entries require a rank."}
                )

            same_rank = ResultEntry.objects.filter(result=result, rank=rank)
            if self.instance is not None:
                same_rank = same_rank.exclude(pk=self.instance.pk)
            if same_rank.exists():
                raise serializers.ValidationError(
                    {"rank": "This rank is already assigned to another entry."}
                )
        else:
            if participant is None:
                raise serializers.ValidationError(
                    {"participant": "Participation entries require a participant."}
                )
            if attrs.get("rank") is not None:
                raise serializers.ValidationError(
                    {"rank": "Participation entries cannot have a rank."}
                )
            if attrs.get("score") is not None:
                raise serializers.ValidationError(
                    {"score": "Participation entries cannot have a score."}
                )
            attrs["rank"] = None
            attrs["score"] = None

        if participant is not None:
            duplicate = ResultEntry.objects.filter(
                result=result, participant=participant
            )
            if self.instance is not None:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise serializers.ValidationError(
                    {"participant": "This participant already has an entry in this result."}
                )

            if not Registration.objects.filter(
                event=result.event,
                participant=participant,
                status="confirmed",
            ).exists():
                raise serializers.ValidationError(
                    {"participant": "This user is not a confirmed participant of this event."}
                )

            if not label:
                label = participant.username

        if not label:
            raise serializers.ValidationError(
                {"label": "Label is required when no participant is selected."}
            )

        attrs["label"] = label
        return attrs


class EventResultSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    entries = ResultEntrySerializer(many=True, read_only=True)

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
        )
        read_only_fields = ("id", "published_at", "entries")

    def validate(self, attrs):
        user = self.context["request"].user

        event = attrs.get("event") or getattr(self.instance, "event", None)
        if event is None:
            raise serializers.ValidationError({"event": "This field is required."})

        if event.organizer != user:
            raise serializers.ValidationError(
                {"event": "You can only manage results for your own events."}
            )

        if self.instance is not None:
            if event != self.instance.event:
                raise serializers.ValidationError(
                    {"event": "Event cannot be changed."}
                )

            if self.instance.is_published:
                modified_fields = set(attrs.keys()) - {"is_published"}
                if modified_fields:
                    raise serializers.ValidationError(
                        "Published results cannot be modified. Unpublish first."
                    )

        is_published = attrs.get(
            "is_published", getattr(self.instance, "is_published", False)
        )

        if is_published and event.status != Event.Status.FINISHED:
            raise serializers.ValidationError(
                {"is_published": "Results can only be published for finished events."}
            )

        return attrs


class PublicResultEntrySerializer(serializers.ModelSerializer):
    participant_username = serializers.SerializerMethodField()

    class Meta:
        model = ResultEntry
        fields = (
            "id",
            "entry_type",
            "participant_username",
            "label",
            "rank",
            "score",
            "notes",
        )

    def get_participant_username(self, obj):
        return obj.participant.username if obj.participant_id else None


class PublicEventResultSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    entries = PublicResultEntrySerializer(many=True, read_only=True)

    class Meta:
        model = EventResult
        fields = (
            "id",
            "event",
            "event_title",
            "summary",
            "published_at",
            "entries",
        )