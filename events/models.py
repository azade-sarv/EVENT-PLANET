from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.aggregates import Avg


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

    @property
    def average_rating(self):
        avg = self.registrations.aggregate(avg=Avg("feedback__rating"))["avg"]
        return round(avg, 2) if avg is not None else None

    @property
    def feedback_count(self):
        return self.registrations.filter(feedback__isnull=False).count()

    @property
    def confirmed_count(self):
        return self.registrations.filter(status="confirmed").count()

    @property
    def available_spots(self):
        return max(self.capacity - self.confirmed_count, 0)

    def clean(self):
        errors = {}

        if self.start_time >= self.end_time:
            errors["end_time"] = "Start time must be before end time."

        if self.capacity < 1:
            errors["capacity"] = "Capacity must be at least 1."

        if self.pk:
            previous_status = (
                type(self).objects
                .filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )

            if previous_status is not None and self.status != previous_status:
                allowed_statuses = self.ALLOWED_TRANSITIONS.get(previous_status, [])
                if self.status not in allowed_statuses:
                    errors["status"] = (
                        f"Cannot transition from {previous_status} "
                        f"to {self.status}."
                    )
        elif self.status != self.Status.DRAFT:
            errors["status"] = "New events must start as Draft."

        if errors:
            raise ValidationError(errors)