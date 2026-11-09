from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from events.models import Event


class Stage(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="stages",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "order"],
                name="unique_stage_order_per_event",
            )
        ]

    def __str__(self):
        return f"{self.event.title} - {self.title}"

    def clean(self):
        if (
            self.start_time
            and self.end_time
            and self.end_time <= self.start_time
        ):
            raise ValidationError(
                "end_time must be after start_time."
            )


class StageRole(models.Model):
    SUGGESTED_ROLES = ["speaker", "judge", "coach"]

    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name="roles",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stage_roles",
    )
    role_type = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["stage", "user", "role_type"],
                name="unique_stage_user_role",
            )
        ]

    def save(self, *args, **kwargs):
        self.role_type = self.role_type.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.role_type} @ {self.stage}"