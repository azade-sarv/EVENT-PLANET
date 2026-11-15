from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from events.models import Event
from registrations.models import Registration


class EventResult(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name="result",
    )
    summary = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Result of {self.event}"

    def save(self, *args, **kwargs):
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        elif not self.is_published:
            self.published_at = None
        super().save(*args, **kwargs)

    def clean(self):
        errors = {}

        if self.is_published:
            if self.event_id is None:
                errors["event"] = "Event is required."
            elif self.event.status != Event.Status.FINISHED:
                errors["is_published"] = (
                    "Results can only be published for finished events."
                )

        if errors:
            raise ValidationError(errors)


class ResultEntry(models.Model):
    class EntryType(models.TextChoices):
        RANKING = "ranking", "Ranking"
        PARTICIPATION = "participation", "Participation"

    result = models.ForeignKey(
        EventResult,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    entry_type = models.CharField(
        max_length=20,
        choices=EntryType.choices,
        default=EntryType.RANKING,
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="result_entries",
    )
    label = models.CharField(max_length=200)
    rank = models.PositiveIntegerField(null=True, blank=True)
    score = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["entry_type", "rank"]
        constraints = [
            models.UniqueConstraint(
                fields=["result", "participant"],
                condition=Q(participant__isnull=False),
                name="unique_participant_per_result",
            ),
            models.UniqueConstraint(
                fields=["result", "rank"],
                condition=Q(rank__isnull=False),
                name="unique_rank_per_result",
            ),
        ]

    def __str__(self):
        return f"[{self.entry_type}] {self.rank or '-'}. {self.label}"

    def clean(self):
        errors = {}

        if self.result_id is None:
            raise ValidationError({"result": "Result is required."})

        if self.result.is_published:
            errors["result"] = "Published results cannot be modified."

        if self.entry_type == self.EntryType.RANKING:
            if self.result.event.event_type != Event.EventType.TOURNAMENT:
                errors["entry_type"] = (
                    "Ranking results are only allowed for tournaments."
                )
            if self.rank is None:
                errors["rank"] = "Ranking entries require a rank."
        else:
            if self.participant_id is None:
                errors["participant"] = (
                    "Participation entries require a participant."
                )
            if self.rank is not None or self.score is not None:
                errors["entry_type"] = (
                    "Participation entries cannot have rank or score."
                )

        if self.participant_id and not Registration.objects.filter(
            event=self.result.event,
            participant_id=self.participant_id,
            status="confirmed",
        ).exists():
            errors["participant"] = (
                "This user is not a confirmed participant of this event."
            )

        if not self.label:
            errors["label"] = "Label is required."

        if errors:
            raise ValidationError(errors)