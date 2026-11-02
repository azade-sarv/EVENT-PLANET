from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Role(models.TextChoices):
        PARTICIPANT = 'PARTICIPANT', 'Participant'
        ORGANIZER = 'ORGANIZER', 'Organizer'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARTICIPANT
    )
