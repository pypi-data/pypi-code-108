from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import SAFE_METHODS

from aparnik.contrib.settings.models import Setting


class IsAdminPermission(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_admin:
            return True
        return False


class IsThirdPartyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        secret_key = get_object_or_404(Setting.objects.active(), key='SECRET_KEY').get_value()
        for method in ['GET', 'POST', 'data']:
            if getattr(request, method, {}).get('secret_key') == secret_key:
                return True
        return False
