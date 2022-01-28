from io import StringIO

from contextlib import contextmanager

from django.contrib.auth.models import User

from germanium.decorators import data_provider
from germanium.tools import assert_equal, assert_false, assert_is_not_none

from security.management import call_command


TRUNCATION_CHAR = '…'


class BaseTestCaseMixin:

    databases = ['default', 'security']

    @data_provider
    def create_user(self, username='test', email='test@localhost'):
        return User.objects._create_user(username, email, 'test', is_staff=True, is_superuser=True)



def test_call_command(*args, **kwargs):
    call_command(*args, **kwargs, stdout=StringIO(), stderr=StringIO())
