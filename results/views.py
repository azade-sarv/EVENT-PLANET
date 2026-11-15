from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from events.models import Event
from users.permissions import IsOrganizer

from .models import EventResult, ResultEntry
from .serializers import (
    EventResultSerializer,
    PublicEventResultSerializer,
    ResultEntrySerializer,
)


class OrganizerEventResultViewSet(viewsets.ModelViewSet):
    serializer_class = EventResultSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return (
            EventResult.objects.filter(event__organizer=self.request.user)
            .select_related("event")
            .prefetch_related("entries__participant")
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_published:
            return Response(
                {"detail": "Published results cannot be deleted. Unpublish first."},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)


class ResultEntryViewSet(viewsets.ModelViewSet):
    serializer_class = ResultEntrySerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        queryset = ResultEntry.objects.filter(
            result__event__organizer=self.request.user
        ).select_related("result__event", "participant")

        result_id = self.request.query_params.get("result")
        if result_id:
            queryset = queryset.filter(result_id=result_id)

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.result.is_published:
            return Response(
                {"detail": "Published results cannot be modified. Unpublish first."},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)


class PublicEventResultViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublicEventResultSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            EventResult.objects.filter(
                event_id=self.kwargs["event_id"],
                is_published=True,
                event__status=Event.Status.FINISHED,
            )
            .select_related("event")
            .prefetch_related("entries__participant")
        )