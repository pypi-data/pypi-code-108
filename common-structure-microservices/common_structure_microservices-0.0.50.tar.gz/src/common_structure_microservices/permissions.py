from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission


class CustomIsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        if request.user == 'INVALIDO':
            raise TokenNotFoundException
        if request.user == 'EXPIRADO':
            raise TokenExpiredException

        return bool(type(request.user) is not AnonymousUser)


class TokenNotFoundException(APIException):
    status_code = 401
    default_detail = 'Token inválido.'
    default_code = 'token_not_found_exception'


class TokenExpiredException(APIException):
    status_code = 401
    default_detail = 'Token expirado.'
    default_code = 'token_expired_exception'
