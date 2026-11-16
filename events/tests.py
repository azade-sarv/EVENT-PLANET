from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from attributes.models import Attribute, EventAttributeValue, EventTypeAttribute
from stages.models import Stage
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
        self.later_stage = Stage.objects.create(
            event=self.event,
            title="Second stage",
            order=2,
            start_time=self.event.start_time + timedelta(hours=2),
            end_time=self.event.start_time + timedelta(hours=3),
        )
        self.earlier_stage = Stage.objects.create(
            event=self.event,
            title="First stage",
            order=1,
            start_time=self.event.start_time + timedelta(hours=1),
            end_time=self.event.start_time + timedelta(hours=2),
        )
        self.client = APIClient()

    def test_public_event_list_and_detail_include_attributes_and_stages(self):
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
        expected_stage_ids = [self.earlier_stage.pk, self.later_stage.pk]
        self.assertEqual(
            [stage["id"] for stage in detail_response.data["stages"]],
            expected_stage_ids,
        )

        list_event = next(
            item for item in list_response.data if item["id"] == self.event.pk
        )
        self.assertCountEqual(list_event["attributes"], expected_attributes)
        self.assertEqual(
            [stage["id"] for stage in list_event["stages"]],
            expected_stage_ids,
        )
