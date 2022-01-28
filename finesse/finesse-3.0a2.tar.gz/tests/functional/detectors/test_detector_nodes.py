"""Integration test cases for detector nodes."""

import pytest
from finesse import Model
from finesse.components import Mirror
from finesse.detectors import PowerDetector


def test_detector_node_cannot_be_added_to_model_when_node_is_not_in_model():
    """Test that a detector cannot have a node not in the same model when added."""
    model_a = Model()
    model_b = Model()

    model_a.add(Mirror("m1"))

    with pytest.raises(Exception):
        model_b.add(PowerDetector("pd1", model_a.m1.p1.o))
