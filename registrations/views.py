from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from events.models import Event
from users.permissions import IsOrganizer, IsParticipant

from .models import Registration
from .serializers import (
    MyRegistrationSerializer,
    ParticipantSerializer,
    RegistrationSerializer,
)


class MyRegistrationsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsParticipant]

    def get_queryset(self):
        return Registration.objects.filter(
            participant=self.request.user
        ).select_related("event").order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return MyRegistrationSerializer
        return RegistrationSerializer

    def perform_create(self, serializer):
        requested_event = serializer.validated_data["event"]

        with transaction.atomic():
            event = Event.objects.select_for_update().get(pk=requested_event.pk)

            if event.status != Event.Status.PUBLISHED:
                raise ValidationError(
                    {"event": "Only published events can be registered."}
                )

            if Registration.objects.filter(
                event=event,
                participant=self.request.user,
            ).exists():
                raise ValidationError(
                    {"event": "You are already registered for this event."}
                )

            confirmed_count = Registration.objects.filter(
                event=event,
                status=Registration.Status.CONFIRMED,
            ).count()
            if confirmed_count >= event.capacity:
                raise ValidationError({"event": "This event is full."})

            serializer.save(event=event, participant=self.request.user)


class EventParticipantsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ParticipantSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        event_id = self.kwargs["event_id"]
        return Registration.objects.filter(
            event_id=event_id,
            event__organizer=self.request.user,
        ).select_related("participant")