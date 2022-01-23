from datetime import date, timedelta

from django.utils import timezone

from aleksis.apps.evalu.models import (
    EvaluationItem,
    EvaluationKeyPair,
    EvaluationPart,
    EvaluationPhase,
    EvaluationRegistration,
    QuestionType,
)
from aleksis.core.models import Group, Person, SchoolTerm


def _get_test_person():
    return Person.objects.get_or_create(first_name="Jane", last_name="Doe")[0]


def _get_test_group():
    return Group.objects.get_or_create(name="Test group")[0]


def _get_test_phase():
    return EvaluationPhase.objects.get_or_create(
        name="Test Phase",
        defaults=dict(
            evaluated_group=_get_test_group(),
            privacy_notice="Some dummy content",
            registration_date_start=date(2020, 1, 1),
            registration_date_end=date(2020, 1, 2),
            evaluation_date_start=date(2020, 1, 3),
            evaluation_date_end=date(2020, 1, 4),
            results_date_start=date(2020, 1, 5),
        ),
    )[0]


def _get_test_evaluation():
    return EvaluationRegistration.objects.create(
        phase=_get_test_phase(),
        person=_get_test_person(),
        privacy_accepted=True,
        privacy_accepted_at=timezone.now(),
        keys=EvaluationKeyPair.create("test"),
    )


def _get_test_school_term():
    school_term, __ = SchoolTerm.objects.get_or_create(
        name="Test", date_start=date(2019, 8, 1), date_end=date(2020, 6, 30)
    )
    return school_term


def _create_some_persons(prefix, n):
    persons = []
    for i in range(n):
        p = Person.objects.create(
            first_name=f"{prefix} First name {i}", last_name=f"{prefix} Last name {i}"
        )
        persons.append(p)
    return persons


def _create_some_empty_groups():
    school_term = _get_test_school_term()
    groups = []
    for i in range(5):
        g = Group.objects.create(name=f"Empty Group {i}", school_term=school_term)
        g.owners.add(_get_test_person())
        groups.append(g)
    return groups


def _create_some_full_groups():
    school_term = _get_test_school_term()
    groups = []
    for i in range(5):
        persons = _create_some_persons("Full Group", 10)
        g = Group.objects.create(name=f"Full Group {i}", school_term=school_term)
        g.members.set(persons)
        g.owners.add(_get_test_person())
        groups.append(g)
    return groups


def _get_test_part():
    return EvaluationPart.objects.get_or_create(name="Foo", defaults=dict(order=1))[0]


def _get_test_item():
    return EvaluationItem.objects.get_or_create(
        part=_get_test_part(),
        defaults=dict(name="Foo", question="Foo?", order=1, item_type=QuestionType.AGREEMENT),
    )[0]
