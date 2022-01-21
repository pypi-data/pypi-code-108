import pytest
from django.contrib.admin.sites import AdminSite
from model_bakery import baker

from mycarehub.clients.admin import ClientAdmin
from mycarehub.clients.models import Client

pytestmark = pytest.mark.django_db


def test_client_admin_get_user_name(user_with_all_permissions):
    admin = ClientAdmin(model=Client, admin_site=AdminSite())
    client = baker.make(Client, user=user_with_all_permissions)
    assert admin.get_user_name(client) == user_with_all_permissions.name
