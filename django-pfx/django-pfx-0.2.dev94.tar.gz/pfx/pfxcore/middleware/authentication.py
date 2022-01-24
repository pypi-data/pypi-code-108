import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse

import jwt
from jwt import DecodeError

logger = logging.getLogger(__name__)


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        authorization = request.headers.get('Authorization')
        if authorization:
            try:
                _, key = authorization.split("Bearer ")
            except ValueError:  # pragma: no cover
                key = None
            try:
                opts = ({"require":  ["exp"]} if settings.PFX_TOKEN_VALIDITY
                        else {})
                decoded = jwt.decode(
                    key, settings.PFX_SECRET_KEY,
                    options=opts,
                    algorithms="HS256")
            except DecodeError as e:
                logger.exception(e)
                return JsonResponse({'message': 'Authentication error'},
                                    status=401)
            except jwt.ExpiredSignatureError:
                return JsonResponse({'message': 'Token has expired'},
                                    status=401)
            except Exception as e:  # pragma: no cover
                logger.exception(e)
                return JsonResponse({'message': 'Authentication error'},
                                    status=500)
            try:
                user = get_user_model()._default_manager.get(
                    pk=decoded['pfx_user_pk'])
            except get_user_model().DoesNotExist:
                return JsonResponse(
                    {'message': 'Authentication error'}, status=401)
            request.user = user
        else:
            request.user = AnonymousUser()

        return self.get_response(request)
