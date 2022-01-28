"""Test parsing of cavity property detectors."""

import pytest
from finesse.script import parse
from finesse.detectors.cavity_detector import CP_KEYWORDS


@pytest.mark.parametrize("keyword,expected", CP_KEYWORDS.items())
def test_cavity_property_detector(keyword, expected):
    model = parse(
        f"""
        m m1 R=0.99 T=0.01 Rc=-0.6
        m m2 R=0.99 T=0.01 Rc=0.6
        s s1 m1.p2 m2.p1 L=1
        cav cav1 m1.p2.o
        cp cav1cp cav1 {keyword}
        """
    )

    assert model.cav1cp.prop == expected
