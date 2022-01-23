import pytest

from aleksis.apps.evalu.models import EvaluationPart, QuestionType

pytestmark = pytest.mark.django_db


def test_str():
    o = EvaluationPart.objects.create(name="Foo", order=1)
    assert str(o) == "Foo"


def test_item_str():
    o = EvaluationPart.objects.create(name="Foo", order=1)
    item = o.items.create(name="Bar", order=1, question="Bar?", item_type=QuestionType.AGREEMENT)
    assert str(item) == "Bar"
