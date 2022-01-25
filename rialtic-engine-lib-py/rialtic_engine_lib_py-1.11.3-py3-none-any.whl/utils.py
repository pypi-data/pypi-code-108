import enum
import json
import uuid
import hashlib

from fhir.resources.fhirtypes import Date
from schema.insight_engine_testcase import InsightEngineTestCase


def unique_identifier(_id: str = ''):
    m = hashlib.sha256()
    m.update(_id.encode('utf-8'))
    prefix = m.hexdigest()
    return prefix[:8] + '-' + str(uuid.uuid4().hex)[:-8]


class _DateUnit(enum.Enum):
    DAY = "day"
    MONTH = "month"
    YEAR = "year"


def test_case_from_file(filename: str) -> InsightEngineTestCase:
    """Do not remove: used by engines."""
    with open(filename) as test_case_file:
        test_case_obj = json.load(test_case_file)
        return InsightEngineTestCase.parse_obj(test_case_obj)


def date_diff(first: Date, second: Date, unit: str) -> int:
    """
    :param unit: one of supported date units: day, month, year
    """
    # No exception handling, because enum exception is fine.
    date_unit = _DateUnit(unit)
    if date_unit == _DateUnit.DAY:
        diff = (first - second).days
    elif date_unit == _DateUnit.MONTH:
        diff = (
            (first.year - second.year) * 12
            + (first.month - second.month)
            - (first.day < second.day)
        )
    elif date_unit == _DateUnit.YEAR:
        diff = (
            first.year
            - second.year
            - ((first.month, first.day) < (second.month, second.day))
        )
    else:
        raise ValueError(f"{unit} unit is not supported")
    return diff
