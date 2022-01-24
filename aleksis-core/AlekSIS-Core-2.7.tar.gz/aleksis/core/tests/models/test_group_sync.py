from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.models import User

import pytest

from aleksis.core.models import Group, Person

pytestmark = pytest.mark.django_db


def test_create():
    Group.objects.create(name="Foo")

    assert DjangoGroup.objects.filter(name="Foo").exists()


def test_assign_members():
    g = Group.objects.create(name="Foo")
    dj_g = DjangoGroup.objects.get(name="Foo")

    u = User.objects.create(username="janedoe")
    p = Person.objects.create(first_name="Jane", last_name="Doe", user=u)

    g.members.add(p)

    assert u in dj_g.user_set.all()


def test_assign_owners():
    g = Group.objects.create(name="Foo")
    dj_g = DjangoGroup.objects.get(name="Foo")

    u = User.objects.create(username="janedoe")
    p = Person.objects.create(first_name="Jane", last_name="Doe", user=u)

    g.owners.add(p)

    assert u in dj_g.user_set.all()


def test_assign_member_of():
    g = Group.objects.create(name="Foo")
    dj_g = DjangoGroup.objects.get(name="Foo")

    u = User.objects.create(username="janedoe")
    p = Person.objects.create(first_name="Jane", last_name="Doe", user=u)

    p.member_of.add(g)

    assert u in dj_g.user_set.all()


def test_assign_owner_of():
    g = Group.objects.create(name="Foo")
    dj_g = DjangoGroup.objects.get(name="Foo")

    u = User.objects.create(username="janedoe")
    p = Person.objects.create(first_name="Jane", last_name="Doe", user=u)

    p.owner_of.add(g)

    assert u in dj_g.user_set.all()
