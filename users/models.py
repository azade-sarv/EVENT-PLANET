
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Role(models.TextChoices):
        PARTICIPANT = "PARTICIPANT", "Participant"
        ORGANIZER = "ORGANIZER", "Organizer"
        SYSTEM = "SYSTEM", "System"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARTICIPANT
    )

    @property
    def is_deleted_user(self):
        return self.username == "deleted_user"

    def __str__(self):
        if self.is_deleted_user:
            return "Deleted User"
        return self.username
