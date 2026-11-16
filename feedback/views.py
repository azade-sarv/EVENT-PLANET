from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from events.models import Event
from registrations.models import Registration
from users.permissions import IsOrganizer, IsParticipant

from .models import Feedback
from .serializers import (
    FeedbackSerializer,
    OrganizerFeedbackSerializer,
    PublicFeedbackSerializer,
)


class MyFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated, IsParticipant]

    def get_queryset(self):
        return Feedback.objects.filter(
            registration__participant=self.request.user
        ).select_related("registration__participant", "registration__event")


class EventFeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrganizerFeedbackSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return Feedback.objects.filter(
            registration__event_id=self.kwargs["event_id"],
            registration__event__organizer=self.request.user,
        ).select_related("registration__participant")


class PublicEventFeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublicFeedbackSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Feedback.objects.filter(
            registration__event_id=self.kwargs["event_id"],
            registration__event__status=Event.Status.FINISHED,
            registration__status=Registration.Status.CONFIRMED,
        ).select_related("registration__participant").order_by("-created_at")