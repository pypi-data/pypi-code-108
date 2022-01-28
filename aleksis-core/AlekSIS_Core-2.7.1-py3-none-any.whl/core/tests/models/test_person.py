import pytest

from aleksis.core.models import Person

pytestmark = pytest.mark.django_db


def test_full_name():
    _person = Person.objects.create(first_name="Jane", last_name="Doe")

    assert _person.full_name == "Doe, Jane"


def test_delete():
    _person = Person.objects.create(first_name="Jane", last_name="Doe")
    _person.delete()
    assert not Person.objects.filter(first_name="Jane", last_name="Doe").exists()
