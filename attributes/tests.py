from datetime import timedelta
from types import SimpleNamespace

from django.test import TestCase
from django.utils import timezone

from events.models import Event
from users.models import User

from .models import Attribute, EventTypeAttribute
from .serializers import AttributeSerializer, EventAttributeValueSerializer


class DefaultAttributeTests(TestCase):
    def test_default_attributes_are_seeded_for_each_event_type(self):
        expected = {
            "webinar": {
                "platform": "string",
                "duration_minutes": "integer",
                "language": "string",
            },
            "tournament": {
                "competition_type": "string",
                "format": "string",
                "registration_deadline": "date",
            },
            "workshop": {
                "has_certificate": "boolean",
                "skill_level": "string",
                "prerequisites": "string",
                "duration_hours": "decimal",
            },
        }

        for event_type, definitions in expected.items():
            actual = dict(
                EventTypeAttribute.objects.filter(event_type=event_type).values_list(
                    "attribute__name",
                    "attribute__data_type",
                )
            )
            self.assertEqual(actual, definitions)


class AttributeSerializerTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizer",
            password="test-password",
            role=User.Role.ORGANIZER,
        )
        self.event = self.create_event("event-one")
        self.other_event = self.create_event("event-two")
        self.request_context = {"request": SimpleNamespace(user=self.organizer)}

    def create_event(self, title):
        now = timezone.now()
        return Event.objects.create(
            organizer=self.organizer,
            title=title,
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=2),
            capacity=10,
        )

    def value_serializer(self, event, attribute, value):
        return EventAttributeValueSerializer(
            data={
                "event": event.pk,
                "attribute": attribute.pk,
                "value": value,
            },
            context=self.request_context,
        )

    def test_event_attribute_cannot_be_used_for_another_event(self):
        attribute = Attribute.objects.create(
            name="Diet",
            data_type=Attribute.DataType.STRING,
            scope=Attribute.Scope.EVENT,
            event=self.event,
        )

        serializer = self.value_serializer(self.other_event, attribute, "Vegan")

        self.assertFalse(serializer.is_valid())
        self.assertIn("attribute", serializer.errors)

    def test_global_attribute_must_be_enabled_for_event_type(self):
        attribute = Attribute.objects.create(
            name="Track",
            data_type=Attribute.DataType.STRING,
            scope=Attribute.Scope.GLOBAL,
        )

        serializer = self.value_serializer(self.event, attribute, "Technology")

        self.assertFalse(serializer.is_valid())
        self.assertIn("attribute", serializer.errors)

    def test_global_attribute_value_is_accepted_when_enabled(self):
        attribute = Attribute.objects.create(
            name="Track",
            data_type=Attribute.DataType.STRING,
            scope=Attribute.Scope.GLOBAL,
        )
        EventTypeAttribute.objects.create(
            event_type=self.event.event_type,
            attribute=attribute,
        )

        serializer = self.value_serializer(self.event, attribute, "Technology")

        self.assertTrue(serializer.is_valid(), serializer.errors)
        value = serializer.save()
        self.assertEqual(value.value, "Technology")

    def test_event_attribute_names_are_unique_per_event(self):
        Attribute.objects.create(
            name="Diet",
            data_type=Attribute.DataType.STRING,
            scope=Attribute.Scope.EVENT,
            event=self.event,
        )
        serializer = AttributeSerializer(
            data={"name": "Diet", "data_type": Attribute.DataType.STRING},
            context={"attribute_event": self.event},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
