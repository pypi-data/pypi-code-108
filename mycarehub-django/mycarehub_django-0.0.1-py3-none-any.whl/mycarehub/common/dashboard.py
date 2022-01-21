from django.contrib.auth import get_user_model

from .models import Facility

User = get_user_model()


def get_mycarehub_facilities_queryset():
    return Facility.objects.mycarehub_facilities().order_by(
        "name",
        "county",
        "mfl_code",
    )


def get_active_facility_count(user):
    return (
        Facility.objects.mycarehub_facilities()
        .filter(
            organisation=user.organisation,
        )
        .count()
    )


def get_active_user_count(user):
    return User.objects.filter(
        is_approved=True,
        approval_notified=True,
        organisation=user.organisation,
    ).count()
