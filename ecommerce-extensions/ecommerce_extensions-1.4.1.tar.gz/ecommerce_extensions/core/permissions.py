"""Custom permissions."""
from rest_framework.permissions import BasePermission

from ecommerce_extensions.core.utils import has_console_access


class HasConsoleAccess(BasePermission):
    """Verify if user has console access."""

    def has_permission(self, request, view):
        return bool(request.user and has_console_access(request.user))
