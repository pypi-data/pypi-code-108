"""Test parsing of beam property detectors."""

import pytest
from finesse.script import parse
from finesse.detectors.bpdetector import BP_KEYWORDS


@pytest.mark.parametrize("keyword,expected", BP_KEYWORDS.items())
def test_beam_property_detector(keyword, expected):
    """Test that beam property detector properties parse correctly."""
    model = parse(
        f"""
        m m1 R=0.99 T=0.01
        bp m1_w m1.p2.o {keyword}
        """
    )

    assert model.m1_w.prop == expected
