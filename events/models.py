from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"
        FINISHED = "finished", "Finished"


    ALLOWED_TRANSITIONS = {
        Status.DRAFT: [Status.PUBLISHED],
        Status.PUBLISHED: [Status.CLOSED],
        Status.CLOSED: [Status.FINISHED],
        Status.FINISHED: [],
    }

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS[self.status]

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

        if self.capacity < 1:
            raise ValidationError("Capacity must be at least 1.")

        if not self.can_transition_to(self.status):
            raise ValidationError(
                f"Cannot transition from {self.status} to {self.status}."
            )