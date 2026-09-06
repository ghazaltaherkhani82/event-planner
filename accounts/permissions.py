from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizer(BasePermission):
    """Allows access only to authenticated users with the ORGANIZER role."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ORGANIZER'
        )


class IsParticipant(BasePermission):
    """Allows access only to authenticated users with the PARTICIPANT role."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'PARTICIPANT'
        )


class IsOrganizerOrReadOnly(BasePermission):
    """Allows organizers to edit, participants/guests to read."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ORGANIZER'
        )