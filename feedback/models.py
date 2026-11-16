from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from events.models import Event
from registrations.models import Registration


class Feedback(models.Model):
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback ({self.rating}/5) for {self.registration}"

    def clean(self):
        if self.registration_id is None:
            raise ValidationError({"registration": "Registration is required."})

        errors = {}

        if self.registration.status != Registration.Status.CONFIRMED:
            errors["registration"] = (
                "Only confirmed registrations can submit feedback."
            )

        if self.registration.event.status != Event.Status.FINISHED:
            errors["rating"] = (
                "Feedback can only be submitted for finished events."
            )

        if errors:
            raise ValidationError(errors)