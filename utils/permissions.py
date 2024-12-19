from rest_framework.permissions import BasePermission


class IsAnonymous(BasePermission):
    """
    Allow anonymous users only.
    """

    def has_permission(self, request, view):
        return request.user.is_anonymous
