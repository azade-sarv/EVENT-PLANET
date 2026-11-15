from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsOrganizer

from .models import Attribute, EventTypeAttribute, EventAttributeValue
from .serializers import (
    AttributeSerializer,
    EventTypeAttributeSerializer,
    EventAttributeValueSerializer,
)


class AttributeViewSet(viewsets.ModelViewSet):
    serializer_class = AttributeSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        queryset = Attribute.objects.filter(scope=Attribute.Scope.GLOBAL)

        event_type = self.request.query_params.get("event_type")
        if event_type:
            queryset = queryset.filter(event_type_links__event_type=event_type)

        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.event_values.exists():
            return Response(
                {"detail": "Cannot update an attribute that is used by events."},
                status=status.HTTP_409_CONFLICT,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.event_values.exists():
            return Response(
                {"detail": "Cannot delete an attribute that is used by events."},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)


class EventTypeAttributeViewSet(viewsets.ModelViewSet):
    queryset = EventTypeAttribute.objects.all()
    serializer_class = EventTypeAttributeSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        event_type = self.request.query_params.get("event_type")
        if event_type:
            return EventTypeAttribute.objects.filter(event_type=event_type)
        return EventTypeAttribute.objects.all()


class EventAttributeValueViewSet(viewsets.ModelViewSet):
    serializer_class = EventAttributeValueSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return EventAttributeValue.objects.filter(
            event__organizer=self.request.user
        ).select_related("event", "attribute")