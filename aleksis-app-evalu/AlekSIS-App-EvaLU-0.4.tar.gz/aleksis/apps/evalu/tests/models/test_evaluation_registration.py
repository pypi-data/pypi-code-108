from django.utils import timezone

import pytest

from aleksis.apps.evalu.models import EvaluationGroup, EvaluationKeyPair, EvaluationRegistration
from aleksis.apps.evalu.tests.models.util import (
    _create_some_empty_groups,
    _create_some_full_groups,
    _create_some_persons,
    _get_test_evaluation,
    _get_test_person,
    _get_test_phase,
    _get_test_school_term,
)
from aleksis.core.models import Group

pytestmark = pytest.mark.django_db


def test_create():
    registration = EvaluationRegistration.objects.create(
        phase=_get_test_phase(),
        person=_get_test_person(),
        privacy_accepted=True,
        privacy_accepted_at=timezone.now(),
        keys=EvaluationKeyPair.create("test"),
    )
    assert registration.pk is not None


def test_str():
    registration = _get_test_evaluation()
    assert "Doe" in str(registration)
    assert "Test Phase" in str(registration)


def test_group_sync():
    empty_groups = _create_some_empty_groups()
    full_groups = _create_some_full_groups()
    registration = _get_test_evaluation()

    assert EvaluationGroup.objects.all().count() == 0
    registration.sync_evaluation_groups()
    assert EvaluationGroup.objects.all().count() == len(full_groups)

    for group in EvaluationGroup.objects.all():
        assert group.registration == registration
        assert group.group
        assert "Full" in group.group_name
        assert group.group in full_groups
        assert group.group not in empty_groups


def _prepare_evaluation_groups():
    empty_groups = _create_some_empty_groups()
    full_groups = _create_some_full_groups()
    registration = _get_test_evaluation()
    registration.sync_evaluation_groups()
    return full_groups, empty_groups, registration


def test_group_sync_rename_one():
    full_groups, empty_groups, registration = _prepare_evaluation_groups()
    person = _get_test_person()

    # Get test group
    one_group = Group.objects.get(name="Full Group 1")

    assert EvaluationGroup.objects.get(group=one_group).group_name == "Full Group 1"

    # Change group and sync
    one_group.name = "Renamed Group"
    one_group.save()
    registration.sync_evaluation_groups()

    assert EvaluationGroup.objects.get(group=one_group).group_name == "Renamed Group"


def test_group_sync_add_one():
    full_groups, empty_groups, registration = _prepare_evaluation_groups()
    person = _get_test_person()

    # Create a new group
    new_group = Group.objects.create(name="New Group", school_term=_get_test_school_term())
    persons = _create_some_persons("New Group", 10)
    new_group.owners.add(person)
    new_group.members.set(persons)

    assert EvaluationGroup.objects.all().count() == len(full_groups)
    registration.sync_evaluation_groups()
    assert EvaluationGroup.objects.all().count() == len(full_groups) + 1


def test_group_sync_delete_one():
    full_groups, empty_groups, registration = _prepare_evaluation_groups()

    # Get test group
    one_group = Group.objects.get(name="Full Group 1")

    assert EvaluationGroup.objects.all().count() == len(full_groups)
    group_count = Group.objects.all().count()

    # Delete groups and sync
    one_group.delete()
    registration.sync_evaluation_groups()

    assert EvaluationGroup.objects.all().count() == len(full_groups)
    assert Group.objects.all().count() == group_count - 1
