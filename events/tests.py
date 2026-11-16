from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from attributes.models import Attribute, EventAttributeValue, EventTypeAttribute
from users.models import User

from .models import Event


class PublicEventAttributeTests(TestCase):
    def setUp(self):
        organizer = User.objects.create_user(
            username="organizer",
            password="test-password",
            role=User.Role.ORGANIZER,
        )
        now = timezone.now()
        self.event = Event.objects.create(
            organizer=organizer,
            title="Public event",
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=2),
            capacity=20,
            status=Event.Status.PUBLISHED,
        )

        default_attribute = Attribute.objects.create(
            name="Track",
            data_type=Attribute.DataType.STRING,
            scope=Attribute.Scope.GLOBAL,
        )
        EventTypeAttribute.objects.create(
            event_type=self.event.event_type,
            attribute=default_attribute,
        )
        EventAttributeValue.objects.create(
            event=self.event,
            attribute=default_attribute,
            value_string="Technology",
        )

        custom_attribute = Attribute.objects.create(
            name="Dress code",
            data_type=Attribute.DataType.STRING,
            scope=Attribute.Scope.EVENT,
            event=self.event,
        )
        EventAttributeValue.objects.create(
            event=self.event,
            attribute=custom_attribute,
            value_string="Business casual",
        )
        self.client = APIClient()

    def test_public_event_list_and_detail_include_default_and_custom_attributes(self):
        expected_attributes = [
            {"name": "Track", "data_type": "string", "value": "Technology"},
            {
                "name": "Dress code",
                "data_type": "string",
                "value": "Business casual",
            },
        ]

        detail_response = self.client.get(f"/api/public/events/{self.event.pk}/")
        list_response = self.client.get("/api/public/events/")

        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(list_response.status_code, 200)
        self.assertCountEqual(detail_response.data["attributes"], expected_attributes)

        list_event = next(
            item for item in list_response.data if item["id"] == self.event.pk
        )
        self.assertCountEqual(list_event["attributes"], expected_attributes)
