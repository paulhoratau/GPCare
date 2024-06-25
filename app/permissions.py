
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners (patients) to view their own prescriptions.
    """

    def has_permission(self, request, view):
        # Allow GET requests (viewing prescriptions) to authenticated users only
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        # Allow owners of the prescription to view it
        return obj.patient == request.user
