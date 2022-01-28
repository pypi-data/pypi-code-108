import logging

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db.models import ManyToManyField, DateField
from django.utils.translation import gettext_lazy as _

from isc_common.auth.models.abstract_base_user import AbstractBaseUser
from isc_common.auth.models.usergroup import UserGroup
from isc_common.common import unknown
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.name_field import NameField
from isc_common.models.audit import AuditModel

logger = logging.getLogger(__name__)


class NonamedUserException(Exception):
    pass


class AbstractUser(AbstractBaseUser, AuditModel):
    username_validator = UnicodeUsernameValidator()

    birthday = DateField(blank = True, null = True)
    first_name = NameField(verbose_name = 'имя')
    last_name = NameField(verbose_name = 'фамилия')
    middle_name = NameField(verbose_name = 'отчетво')
    usergroup = ManyToManyField(UserGroup, verbose_name = 'группы')
    username = CodeStrictField(verbose_name = 'логин', unique = True, validators = [username_validator], error_messages = {'unique': "Такой пользователь уже существует.", }, )

    @property
    def is_admin(self):
        res = False
        for group in self.usergroup.all():
            if group.is_admin:
                res = True
                break
        return res

    @property
    def is_develop(self):
        res = False
        for group in self.usergroup.all():
            if group.is_develop:
                res = True
                break
        return res

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def get_full_name(self):
        return f'{self.last_name.strip() if self.last_name else self.username} ' \
               f'{self.first_name.strip() if self.first_name else ""} ' \
               f'{self.middle_name.strip() if self.middle_name else ""}'

    @classmethod
    def full_name(cls, first_name, middle_name, last_name, birthday = None, translit = False):
        if first_name is None and middle_name is None and last_name is None:
            raise NonamedUserException('first_name is None and middle_name is None and last_name is None')

        res = f'{last_name.strip()}' \
              f'{first_name.strip() if first_name else ""} ' \
              f'{middle_name.strip() if middle_name else ""} ' \
              f'{birthday if birthday else ""}'
        if translit is True:
            return AuditModel.translit(res.strip())
        return res.strip()

    @classmethod
    def short_name(cls, first_name, middle_name, last_name, translit = False):
        from isc_common.models.audit import AuditModel

        if first_name is None and middle_name is None and last_name is None:
            raise Exception('first_name is None and middle_name is None and last_name is None')

        fn = f'{first_name.strip()[0:1].upper() if first_name else ""}'
        if fn != '':
            fn = ' ' + fn + '.'

        mn = f'{middle_name.strip()[0:1].upper() if middle_name else ""}'
        if mn != '':
            mn = ' ' + mn + '.'

        if last_name is not None:
            res = f'{last_name.strip()} {fn}{mn}'
        else:
            res = f'{fn}{mn}'

        if translit is True:
            return AuditModel.translit(res.strip())

        return res.strip()

    @property
    def get_short_name(self):
        username = self.username if self.username != unknown else ''

        fn = f'{self.first_name.strip()[0:1].upper() if self.first_name else ""}'
        if fn != '':
            fn = ' ' + fn + '.'

        mn = f'{self.middle_name.strip()[0:1].upper() if self.middle_name else ""}'
        if mn != '':
            mn = ' ' + mn + '.'

        res = f'{self.last_name.strip() if self.last_name else username}{fn}{mn}'
        if res.strip() == "":
            res = username
        return res.strip()

    @property
    def get_short_name1(self):
        res = f'{self.first_name.strip()[0:1].upper() if self.first_name else ""} ' \
              f'{self.middle_name.strip()[0:1].upper() if self.middle_name else ""}'
        if res.strip() == "":
            if self.username != unknown:
                res = self.username
            else:
                res = ''
        return res.strip()

    def user_short_name(self):
        return self.get_short_name

    def email_user(self, subject, message, from_email = None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
