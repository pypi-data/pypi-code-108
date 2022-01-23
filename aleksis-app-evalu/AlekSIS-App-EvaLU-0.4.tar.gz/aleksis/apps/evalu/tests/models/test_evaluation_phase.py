from datetime import date

from django.core.exceptions import ValidationError

import pytest
from freezegun import freeze_time

from aleksis.apps.evalu.tests.models.util import _get_test_phase

pytestmark = pytest.mark.django_db


def test_create():
    phase = _get_test_phase()
    phase.save()

    assert phase.pk is not None


def test_clean_registration_date_start_before_end():
    phase = _get_test_phase()

    phase.clean()  # Correct result

    phase.registration_date_start = date(2020, 1, 2)
    phase.registration_date_end = date(2020, 1, 1)
    with pytest.raises(ValidationError):
        phase.clean()


def test_clean_evaluation_date_start_before_registration_date_end():
    phase = _get_test_phase()

    phase.registration_date_start = date(2020, 1, 1)
    phase.registration_date_end = date(2020, 1, 2)
    phase.evaluation_date_start = date(2020, 1, 2)
    phase.evaluation_date_end = date(2020, 1, 3)
    phase.clean()

    phase.evaluation_date_start = date(2020, 1, 1)
    with pytest.raises(ValidationError):
        phase.clean()

    phase.evaluation_date_start = date(2020, 1, 3)
    phase.clean()


def test_clean_evaluation_date_start_before_date_end():
    phase = _get_test_phase()

    phase.evaluation_date_start = date(2020, 1, 3)
    phase.evaluation_date_end = date(2020, 1, 4)
    phase.results_date_start = date(2020, 1, 3)
    with pytest.raises(ValidationError):
        phase.clean()

    phase.results_date_start = date(2020, 1, 4)
    with pytest.raises(ValidationError):
        phase.clean()

    phase.results_date_start = date(2020, 1, 5)
    phase.clean()  # Correct result


def test_clean_results_date_start_before_evaluation_date_end():
    phase = _get_test_phase()

    phase.evaluation_date_start = date(2020, 1, 3)
    phase.evaluation_date_end = date(2020, 1, 2)
    phase.results_date_start = date(2020, 1, 3)
    phase.results_date_end = date(2020, 1, 2)
    with pytest.raises(ValidationError):
        phase.clean()

    phase.results_date_start = date(2020, 1, 2)
    phase.results_date_end = date(2020, 1, 3)


def test_evaluation_status():
    phase = _get_test_phase()
    phase.registration_date_start = date(2020, 1, 1)
    phase.registration_date_end = date(2020, 1, 2)
    phase.evaluation_date_start = date(2020, 1, 4)
    phase.evaluation_date_end = date(2020, 1, 5)
    phase.results_date_start = date(2020, 1, 7)

    with freeze_time("2019-12-31"):
        assert phase.status == "not_started"
    with freeze_time("2020-01-01"):
        assert phase.status == "not_started"
        assert phase.registration_running
    with freeze_time("2020-01-02"):
        assert phase.status == "not_started"
        assert phase.registration_running
    with freeze_time("2020-01-03"):
        assert phase.status == "not_started"
        assert not phase.registration_running
    with freeze_time("2020-01-04"):
        assert phase.status == "evaluation"
    with freeze_time("2020-01-05"):
        assert phase.status == "evaluation"
    with freeze_time("2020-01-06"):
        assert phase.status == "evaluation_closed"
    with freeze_time("2020-01-07"):
        assert phase.status == "results"
    with freeze_time("2020-01-08"):
        assert phase.status == "results"


def test_str():
    phase = _get_test_phase()
    assert str(phase) == "Test Phase"
