from rest_framework.permissions import BasePermission

from .models import User


class BaseRolePermission(BasePermission):
    allowed_roles = ()
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role in self.allowed_roles


class IsOrganizer(BaseRolePermission):
    allowed_roles = (User.Role.ORGANIZER,)
    message = "Only organizers can access this endpoint."


class IsParticipant(BaseRolePermission):
    allowed_roles = (User.Role.PARTICIPANT,)
    message = "Only participants can access this endpoint."


class IsSystem(BaseRolePermission):
    allowed_roles = (User.Role.SYSTEM,)
    message = "Only system accounts can access this endpoint."