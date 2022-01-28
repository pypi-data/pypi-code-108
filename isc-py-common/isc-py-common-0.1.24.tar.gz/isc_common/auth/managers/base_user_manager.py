import logging

from django.utils.crypto import get_random_string

from isc_common.models.audit import AuditQuerySet, AuditManager

logger = logging.getLogger(__name__)


class BaseUserQuerySet(AuditQuerySet):
    def getRecord(self, record):
        res = {
            "id": record.id,
            "username": record.username,
            "first_name": record.first_name,
            "last_name": record.last_name,
            "middle_name": record.middle_name,
            "email": record.email,
            "password": record.password,
            "last_login": record.last_login,
            "deliting": record.deliting,
            "editing": record.editing,
        }
        return res


class BaseUserManager(AuditManager):

    def get_queryset(self):
        return BaseUserQuerySet(self.model, using=self._db).filter(deleted_at=None)

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = email_name + '@' + domain_part.lower()
        return email

    def make_random_password(self, length=10,
                             allowed_chars='abcdefghjkmnpqrstuvwxyz'
                                           'ABCDEFGHJKLMNPQRSTUVWXYZ'
                                           '23456789'):
        """
        Generate a random password with the given length and given
        allowed_chars. The default value of allowed_chars does not have "I" or
        "O" or letters and digits that look similar -- just to avoid confusion.
        """
        return get_random_string(length, allowed_chars)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})
