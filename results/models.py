from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from events.models import Event


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

    def __str__(self):
        return f"[{self.entry_type}] {self.rank or '-'}. {self.label}"

    def clean(self):
        T = self.EntryType
        if self.entry_type == T.RANKING and self.rank is None:
            raise ValidationError("Ranking entries require a rank.")
        if self.entry_type == T.PARTICIPATION:
            if self.participant is None:
                raise ValidationError("Participation entries require a participant.")
            if self.rank is not None or self.score is not None:
                raise ValidationError(
                    "Participation entries cannot have rank or score."
                )