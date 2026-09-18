from rest_framework.permissions import BasePermission


class IsInstructor(BasePermission):
    """Allow access only to users with the instructor role (or staff)."""

    message = "Instructor role required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_instructor()
