from django.conf import settings
from django.urls import reverse

import pytest

pytestmark = pytest.mark.django_db


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
