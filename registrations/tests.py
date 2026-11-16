from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from events.models import Event
from users.models import User

from .models import Registration
from .views import MyRegistrationsViewSet


class RegistrationCapacityTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizer",
            password="test-password",
            role=User.Role.ORGANIZER,
        )
        self.existing_participant = User.objects.create_user(
            username="participant-one",
            password="test-password",
        )
        self.new_participant = User.objects.create_user(
            username="participant-two",
            password="test-password",
        )
        now = timezone.now()
        self.event = Event.objects.create(
            organizer=self.organizer,
            title="Full event",
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=2),
            capacity=1,
            status=Event.Status.PUBLISHED,
        )
        Registration.objects.create(
            event=self.event,
            participant=self.existing_participant,
        )

    def test_create_rechecks_capacity_after_serializer_validation(self):
        view = MyRegistrationsViewSet()
        view.request = SimpleNamespace(user=self.new_participant)
        serializer = Mock()
        serializer.validated_data = {"event": self.event}

        with self.assertRaises(ValidationError):
            view.perform_create(serializer)

        serializer.save.assert_not_called()

# Create your tests here.
