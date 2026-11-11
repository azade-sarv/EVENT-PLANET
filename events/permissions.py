from rest_framework.permissions import BasePermission

from .models import Event


class IsEventOwner(BasePermission):
    message = "You can only manage your own events."

    owner_relations = ("event", "stage", "registration", "result")

    def has_object_permission(self, request, view, obj):
        event = self.get_event(obj)
        return event is not None and event.organizer_id == request.user.id

    def get_event(self, obj):
        if isinstance(obj, Event):
            return obj

        for relation in self.owner_relations:
            parent = getattr(obj, relation, None)
            if parent is not None:
                return self.get_event(parent)

        return None