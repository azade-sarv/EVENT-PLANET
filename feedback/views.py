from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.permissions import IsParticipant

from .models import Feedback
from .serializers import FeedbackSerializer, PublicFeedbackSerializer


class MyFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated, IsParticipant]

    def get_queryset(self):
        return Feedback.objects.filter(
            registration__participant=self.request.user
        ).select_related("registration__participant", "registration__event")

    def perform_create(self, serializer):
        registration_id = self.request.data.get("registration")
        from registrations.models import Registration
        registration = Registration.objects.get(
            id=registration_id,
            participant=self.request.user
        )
        serializer.save(registration=registration)


class EventFeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublicFeedbackSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        event_id = self.kwargs["event_id"]
        return Feedback.objects.filter(
            registration__event_id=event_id,
            registration__event__status="finished",
        ).select_related("registration__participant")