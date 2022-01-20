import pytest
from iguanas.rule_selection import SimpleFilter
from iguanas.pipeline import ClassAccessor
from iguanas.metrics import FScore


def test_get():
    f1 = FScore(1)
    sf = SimpleFilter(
        threshold=0.05,
        operator='>=',
        metric=f1.fit
    )
    ca = ClassAccessor('sf', 'rules_to_keep')
    sf.rules_to_keep = ['Rule1']
    steps = [
        ('sf', sf),
    ]
    assert ca.get(steps) == ['Rule1']


def test_error():
    f1 = FScore(1)
    sf = SimpleFilter(
        threshold=0.05,
        operator='>=',
        metric=f1.fit
    )
    ca = ClassAccessor('sf3', 'rules_to_keep')
    sf.rules_to_keep = ['Rule1']
    steps = [
        ('sf', sf),
    ]
    with pytest.raises(ValueError, match='There are no steps in `pipeline` corresponding to `class_tag`=sf3'):
        ca.get(steps)
