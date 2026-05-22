from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Registration


class IsOrganizer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'organizer'
        )


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True

        return obj.organizer == request.user


class IsConfirmedAttendee(BasePermission):
    def has_permission(self, request, view):

        event_id = view.kwargs.get('event_pk')

        return Registration.objects.filter(
            user=request.user,
            event_id=event_id,
            status='confirmed'
        ).exists()