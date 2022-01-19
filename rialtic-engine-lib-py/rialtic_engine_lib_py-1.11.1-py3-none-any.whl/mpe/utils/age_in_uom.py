import math
import datetime as dt

from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.errors import ClaimError


def yyyymmdd_to_date(yyyymmdd: str) -> dt.date:
    try:
        year, month, day = int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8])
    except (IndexError, ValueError):
        raise ValueError(f'Internal error: wrong date format in reference data set '
                         f'({yyyymmdd} was supposed to be in the form YYYYMMDD).')

    return dt.date(year=year, month=month, day=day)


def get_patient_age_in_days(clf: ClaimLineFocus) -> int:
    """ClaimLineFocus.patient_age returns the age in years.
    So we had to rewrite the code."""
    try:
        birth = clf.patient.birthDate
        start, _ = clf.service_period
        return (start - birth).days
    except AttributeError:
        raise ClaimError(f"Birth date not found for patient with id {clf.patient.id}.")


def days_to_uom(days: int, uom: str) -> int:
    """|Patient Age| - patient age should be calculated in years, months, and days.
    The value used should match the uom field for the age field that is being used in logic.
    1. Patient age in years = (<lineServicedDateFrom> - <patientBirthDate>)/365), whole number, do not round up
    2. patient age in months = ((<lineServicedDateFrom - <patientBirthDate>)/30.436, whole number, do not round up
    3. patient age in days = (<lineServicedDateFrom> - <patientBirthDate>)
    """
    if uom.startswith('day'):
        return days
    if uom.startswith('month'):
        return math.floor(days / 30.436)
    if uom.startswith('year'):
        return math.floor(days / 365.0)
