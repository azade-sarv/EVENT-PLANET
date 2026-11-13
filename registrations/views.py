from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
        serializer.save(participant=self.request.user)


class EventParticipantsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ParticipantSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        event_id = self.kwargs["event_id"]
        return Registration.objects.filter(
            event_id=event_id,
            event__organizer=self.request.user,
        ).select_related("participant")