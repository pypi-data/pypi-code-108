from django.db.models import Q
from django.utils import timezone

from rules import predicate

from aleksis.apps.evalu.models import EvaluationGroup, EvaluationPhase


@predicate
def is_member_of_any_evaluation_group(user):
    return EvaluationPhase.objects.filter(evaluated_group__members=user.person).exists()


@predicate
def is_member_of_evaluated_group(user, obj):
    print(obj)
    return user.person in obj.evaluated_group.members.all()


@predicate
def is_evaluated_person(user, obj):
    return user.person == obj.person


@predicate
def is_registration_running(user, obj):
    if hasattr(obj, "phase"):
        return obj.phase.registration_running
    return obj.registration_running


def is_evaluation_status(status):
    name = f"is_evaluation_status:{status}"

    @predicate(name)
    def fn(user, obj):
        if hasattr(obj, "phase"):
            return obj.phase.status == status
        return obj.status == status

    return fn


def is_evaluation_status_for_group(status):
    name = f"is_evaluation_status_for_group:{status}"

    @predicate(name)
    def fn(user, obj):
        return obj.registration.phase.status == status

    return fn


@predicate
def is_evaluated_person_for_group(user, obj):
    return user.person == obj.registration.person


@predicate
def is_participant_for_group(user, obj):
    if not obj.group:
        return False
    return user.person in obj.group.members.all()


@predicate
def is_unlocked(user, obj):
    return obj.is_unlocked


@predicate
def has_any_evaluation_group(user, obj):
    now_date = timezone.now().date()
    return (
        EvaluationGroup.objects.filter(
            Q(group__members=user.person) | Q(done_evaluations__evaluated_by=user.person)
        )
        .filter(registration__phase__evaluation_date_start__lte=now_date)
        .exists()
    )


@predicate
def is_finishing_possible(user, obj):
    return obj.finishing_possible


@predicate
def is_finished(user, obj):
    if hasattr(obj, "registration"):
        return obj.registration.finished
    return obj.finished
