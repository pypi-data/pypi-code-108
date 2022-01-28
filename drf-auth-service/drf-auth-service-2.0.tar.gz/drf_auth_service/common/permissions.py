from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from drf_auth_service.models import Service


class ServiceTokenPermission(BasePermission):

    @staticmethod
    def get_token(request):
        return request.headers.get('Service-Token', None)

    def has_permission(self, request, view):
        token = self.get_token(request)

        if token is None:
            raise PermissionDenied("Service-Token is missing")

        request.service = Service.objects.filter(public_token=token).first()

        if not request.service:
            raise PermissionDenied("Invalid Service-Token")

        return True


class SecretServiceTokenPermission(BasePermission):

    @staticmethod
    def get_tokens(request):
        return request.headers.get('Service-Token', None), request.headers.get('Secret-Token', None)

    def has_permission(self, request, view):
        service_token, secret_token = self.get_tokens(request)

        if service_token is None:
            raise PermissionDenied("Service-Token is missing")

        if secret_token is None:
            raise PermissionDenied("Secret-Token is missing")

        request.service = Service.objects.filter(public_token=service_token, secret_token=secret_token).first()

        if not request.service:
            raise PermissionDenied("Invalid Service-Token")

        return True
