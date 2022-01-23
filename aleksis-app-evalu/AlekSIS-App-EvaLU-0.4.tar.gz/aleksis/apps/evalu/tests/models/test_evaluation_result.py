import pytest

from aleksis.apps.evalu.models import (
    EvaluationGroup,
    EvaluationPart,
    EvaluationResult,
    QuestionType,
)
from aleksis.apps.evalu.tests.models.util import _get_test_evaluation, _get_test_item

pytestmark = pytest.mark.django_db


def test_store_int():
    registration = _get_test_evaluation()
    item = _get_test_item()
    group = EvaluationGroup.objects.create(
        registration=registration,
        group_name="Test Group",
    )

    result = EvaluationResult(group=group, item=item)
    assert result.result == ""

    result.store_result(10)
    assert result.result != ""
    assert result.result != "10"

    assert result.get_result("test") == 10


def test_store_str():
    registration = _get_test_evaluation()
    item = _get_test_item()
    item.item_type = QuestionType.FREE_TEXT
    item.save()
    group = EvaluationGroup.objects.create(
        registration=registration,
        group_name="Test Group",
    )

    result = EvaluationResult(group=group, item=item)
    assert result.result == ""

    result.store_result("I am a string")
    assert result.result != ""
    assert result.result != "I am a string"

    assert result.get_result("test") == "I am a string"


LONG_STR = """
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, 
sed diam nonumy eirmod tempor invidunt ut labore et dolore 
magna aliquyam erat, sed diam voluptua. At vero eos et accusam 
et justo duo dolores et ea rebum. Stet clita kasd gubergren, 
no sea takimata sanctus est Lorem ipsum dolor sit amet. 
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, 
sed diam nonumy eirmod tempor invidunt ut labore et dolore 
magna aliquyam erat, sed diam voluptua. 
At vero eos et accusam et justo duo dolores et ea rebum. 
Stet clita kasd gubergren, 
no sea takimata sanctus est Lorem ipsum dolor sit amet.
"""


def test_store_too_long_str():
    registration = _get_test_evaluation()
    item = _get_test_item()
    item.item_type = QuestionType.FREE_TEXT
    item.save()
    group = EvaluationGroup.objects.create(
        registration=registration,
        group_name="Test Group",
    )

    result = EvaluationResult(group=group, item=item)
    assert result.result == ""

    result.store_result(LONG_STR)

    assert result.result != ""
    assert result.result != LONG_STR

    assert result.get_result("test") == LONG_STR
