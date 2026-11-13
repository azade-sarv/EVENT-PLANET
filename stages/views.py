from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsOrganizer

from .models import Stage, StageRole
from .serializers import StageSerializer, StageRoleSerializer


class StageViewSet(viewsets.ModelViewSet):
    serializer_class = StageSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return Stage.objects.filter(
            event__organizer=self.request.user
        ).select_related("event").prefetch_related("roles__user").order_by("event", "order")


class StageRoleViewSet(viewsets.ModelViewSet):
    serializer_class = StageRoleSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return StageRole.objects.filter(
            stage__event__organizer=self.request.user
        ).select_related("stage", "user")