import binascii
import os
from typing import Any, Optional, Tuple

from django.conf import settings
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from simple_graphql.auth.exceptions import AuthenticationException


class AuthenticationSession(models.Model):
    objects: "Manager[AuthenticationSession]"

    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="authentication_sessions",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    datetime_created = models.DateTimeField(_("Datetime created"), auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.key[:5]}{'*' * len(self.key[5:])}"

    @classmethod
    def generate_key(cls) -> str:
        return binascii.hexlify(os.urandom(20)).decode()

    @classmethod
    def create_for_user(cls, user: Any) -> "AuthenticationSession":
        return cls.objects.create(user=user, key=cls.generate_key())

    @classmethod
    def authenticate(cls, key: str) -> Optional[Tuple[Any, Any]]:
        try:
            token = cls.objects.select_related("user").get(key=key)
        except cls.DoesNotExist:
            raise AuthenticationException(_("Invalid token."))

        if not token.user.is_active:
            raise AuthenticationException(_("Invalid token."))

        return (token.user, token)
