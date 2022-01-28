from django.contrib.auth import get_user_model

import pytest

from aleksis.core.models import Group, Person

pytestmark = pytest.mark.django_db


def test_all_settigns_registered():
    """Tests for regressions of preferences not being registered.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/592
    """

    from dynamic_preferences.types import BasePreferenceType

    from aleksis.core import preferences
    from aleksis.core.preferences import person_preferences_registry, site_preferences_registry

    for obj in preferences.__dict__.values():
        if not isinstance(obj, BasePreferenceType):
            continue

        in_site_reg = site_preferences_registry.get(obj.section.name, {}).get(obj.name, None) is obj
        in_person_reg = (
            person_preferences_registry.get(obj.section.name, {}).get(obj.name, None) is obj
        )

        assert in_site_reg != in_person_reg


def test_custom_managers_return_correct_qs():
    """Tests that custom managers' get_queryset methods return the expected qs.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/594
    """

    from aleksis.core import managers

    def _check_get_queryset(Manager, QuerySet):
        assert isinstance(Manager.from_queryset(QuerySet)().get_queryset(), QuerySet)

    _check_get_queryset(managers.GroupManager, managers.GroupQuerySet)


def test_reassign_user_to_person():
    """Tests that on re-assigning a user, groups are correctly synced.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/628
    """

    User = get_user_model()

    group1 = Group.objects.create(name="Group 1")
    group2 = Group.objects.create(name="Group 2")

    user1 = User.objects.create(username="user1")
    user2 = User.objects.create(username="user2")

    person1 = Person.objects.create(first_name="Person", last_name="1", user=user1)
    person2 = Person.objects.create(first_name="Person", last_name="2", user=user2)

    person1.member_of.set([group1])
    person2.member_of.set([group2])

    assert user1.groups.count() == 1
    assert user2.groups.count() == 1
    assert user1.groups.first().name == "Group 1"
    assert user2.groups.first().name == "Group 2"

    person1.user = None
    person1.save()
    assert user1.groups.count() == 0

    person2.user = user1
    person2.save()
    person1.user = user2
    person1.save()

    assert user1.groups.count() == 1
    assert user2.groups.count() == 1
    assert user1.groups.first().name == "Group 2"
    assert user2.groups.first().name == "Group 1"
