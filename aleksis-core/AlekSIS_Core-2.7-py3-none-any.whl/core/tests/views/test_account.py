from django.conf import settings
from django.test import override_settings
from django.urls import reverse

import ldap
import pytest
from django_auth_ldap.config import LDAPSearch

from aleksis.core.models import UserAdditionalAttributes

pytestmark = pytest.mark.django_db

LDAP_BASE = "dc=example,dc=com"
LDAP_SETTINGS = {
    "AUTH_LDAP_GLOBAL_OPTIONS": {
        ldap.OPT_NETWORK_TIMEOUT: 1,
    },
    "AUTH_LDAP_USER_SEARCH": LDAPSearch(LDAP_BASE, ldap.SCOPE_SUBTREE),
}


def test_index_not_logged_in(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response["Location"].startswith(reverse(settings.LOGIN_URL))


def test_login_without_person(client, django_user_model):
    username = "foo"
    password = "bar"

    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)

    response = client.get("/", follow=True)

    assert response.status_code == 200
    assert "Your user account is not linked to a person." in response.content.decode("utf-8")


def test_logout(client, django_user_model):
    username = "foo"
    password = "bar"

    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)

    response = client.get("/", follow=True)
    assert response.status_code == 200

    response = client.get(reverse("logout"), follow=True)

    assert response.status_code == 200
    assert "Please login to see this page." in response.content.decode("utf-8")


@override_settings(
    AUTHENTICATION_BACKENDS=[
        "aleksis.core.util.ldap.LDAPBackend",
        "django.contrib.auth.backends.ModelBackend",
    ],
    AUTH_LDAP_SERVER_URI="ldap://[100::0]",
    AUTH_LDAP_SET_USABLE_PASSWORD=True,
    **LDAP_SETTINGS
)
def test_login_ldap_fail_if_previously_ldap_authenticated(client, django_user_model):
    username = "foo"
    password = "bar"

    django_user_model.objects.create_user(username=username, password=password)

    # Logging in with a fresh account should success
    res = client.login(username=username, password=password)
    assert res
    client.get(reverse("logout"), follow=True)

    # Logging in with a previously LDAP-authenticated account should fail
    UserAdditionalAttributes.set_user_attribute(username, "ldap_authenticated", True)
    res = client.login(username=username, password=password)
    assert not res

    # Explicitly noting account has not been used with LDAP should succeed
    UserAdditionalAttributes.set_user_attribute(username, "ldap_authenticated", False)
    res = client.login(username=username, password=password)
    assert res
