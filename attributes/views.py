from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from events.models import Event
from users.permissions import IsOrganizer

from .models import Attribute, EventAttributeValue, EventTypeAttribute
from .serializers import (
    AttributeSerializer,
    EventTypeAttributeSerializer,
    EventAttributeValueSerializer,
)


class AttributeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttributeSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        queryset = Attribute.objects.filter(scope=Attribute.Scope.GLOBAL)

        event_type = self.request.query_params.get("event_type")
        if event_type:
            queryset = queryset.filter(event_type_links__event_type=event_type)

        return (
            queryset.prefetch_related("event_type_links")
            .distinct()
            .order_by("name")
        )


class EventTypeAttributeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventTypeAttributeSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        queryset = EventTypeAttribute.objects.filter(
            attribute__scope=Attribute.Scope.GLOBAL
        ).select_related("attribute")

        event_type = self.request.query_params.get("event_type")
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        return queryset.order_by("event_type", "attribute__name")


class EventCustomAttributeViewSet(viewsets.ModelViewSet):
    serializer_class = AttributeSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return Attribute.objects.filter(
            scope=Attribute.Scope.EVENT,
            event_id=self.kwargs["event_id"],
            event__organizer=self.request.user,
        ).order_by("name")

    def get_event(self):
        return get_object_or_404(
            Event,
            pk=self.kwargs["event_id"],
            organizer=self.request.user,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["attribute_event"] = self.get_event()
        return context

    def perform_create(self, serializer):
        serializer.save(
            scope=Attribute.Scope.EVENT,
            event=serializer.context["attribute_event"],
        )

    def perform_update(self, serializer):
        serializer.save(
            scope=Attribute.Scope.EVENT,
            event=serializer.instance.event,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.event_values.exists():
            return Response(
                {"detail": "Delete the value of this attribute first."},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)


class EventAttributeValueViewSet(viewsets.ModelViewSet):
    serializer_class = EventAttributeValueSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        queryset = EventAttributeValue.objects.filter(
            event__organizer=self.request.user
        ).select_related("event", "attribute")

        event_id = self.request.query_params.get("event")
        if event_id:
            try:
                event_id = int(event_id)
            except (TypeError, ValueError) as exc:
                raise ValidationError(
                    {"event": "A valid integer is required."}
                ) from exc

            if event_id < 1:
                raise ValidationError(
                    {"event": "A valid positive integer is required."}
                )

            queryset = queryset.filter(event_id=event_id)

        return queryset.order_by("event_id", "attribute__name")