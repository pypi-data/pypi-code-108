from typing import Union

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from expressmoney import adapters
from expressmoney.adapters import Request

User = get_user_model()


class DjangoTasks(adapters.Tasks):

    def __init__(self,
                 service: str = 'default',
                 path: str = '/',
                 user: Union[None, int, User] = None,
                 project: str = settings.PROJECT,
                 queue: str = 'attempts-1',
                 location: str = 'europe-west1',
                 in_seconds: int = None):
        user = None if user is None else user if isinstance(user, User) else User.objects.get(pk=user)
        access_token = RefreshToken.for_user(user).access_token if user is not None else None
        super().__init__(service, path, access_token, project, queue, location, in_seconds)


class DjangoPubSub(adapters.PubSub):

    def __init__(self, topic_id: str, user: Union[None, int, User] = None, project: str = settings.PROJECT):
        user = None if user is None else user if isinstance(user, User) else User.objects.get(pk=user)
        access_token = RefreshToken.for_user(user).access_token if user is not None else None
        super().__init__(topic_id, access_token, project)


class DjangoRequest(Request):

    def __init__(self,
                 service: str = None,
                 path: str = '/',
                 user: Union[None, int, User] = None,
                 project: str = 'expressmoney',
                 timeout: tuple = (30, 30),
                 ):
        user = None if user is None else user if isinstance(user, User) else User.objects.get(pk=user)
        access_token = RefreshToken.for_user(user).access_token if user is not None else None
        super().__init__(service, path, access_token, project, timeout)

    def _get_authorization(self) -> dict:
        from google.auth.transport.requests import Request
        from google.oauth2 import id_token
        authorization = super()._get_authorization()
        open_id_connect_token = id_token.fetch_id_token(Request(), self._aud)
        iap_token = {'Authorization': f'Bearer {open_id_connect_token}'}
        authorization.update(iap_token)
        return authorization
