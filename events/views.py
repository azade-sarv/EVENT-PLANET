from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .mixins import OwnedEventQuerysetMixin
from .models import Event
from .permissions import IsEventOwner
from .serializers import EventSerializer, EventStatusSerializer, PublicEventSerializer
from users.permissions import IsOrganizer


class OrganizerEventViewSet(OwnedEventQuerysetMixin, viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by("-created_at")
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrganizer, IsEventOwner]
    event_owner_lookup = "organizer"

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=["post"], url_path="status")
    def change_status(self, request, pk=None):
        event = self.get_object()
        serializer = EventStatusSerializer(event, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(EventSerializer(event).data)

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        if event.status != Event.Status.DRAFT:
            return Response(
                {"detail": "Only draft events can be deleted."},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)


class PublicEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublicEventSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Event.objects.filter(
            status=Event.Status.PUBLISHED
        ).order_by("start_time") 