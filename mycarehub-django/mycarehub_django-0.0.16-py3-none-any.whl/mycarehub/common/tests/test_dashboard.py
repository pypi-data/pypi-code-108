import random

import pytest
from django.contrib.auth import get_user_model
from faker.proxy import Faker
from model_bakery import baker

from mycarehub.common.constants import WHITELIST_COUNTIES
from mycarehub.common.dashboard import get_active_facility_count, get_active_user_count
from mycarehub.common.models import Facility

User = get_user_model()

pytestmark = pytest.mark.django_db

fake = Faker()


def test_get_active_facility_count(user):
    baker.make(
        Facility,
        county=random.choice(WHITELIST_COUNTIES),
        active=True,
        organisation=user.organisation,
    )
    assert get_active_facility_count(user) == 1


def test_get_active_user_count(user):
    baker.make(
        User,
        is_approved=True,
        approval_notified=True,
        organisation=user.organisation,
    )
    assert get_active_user_count(user) >= 1
