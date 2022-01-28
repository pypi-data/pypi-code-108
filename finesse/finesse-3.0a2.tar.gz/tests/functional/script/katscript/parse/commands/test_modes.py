"""Test modes command parsing."""

import numpy as np


def test_modes(model):
    """Test that the modes command parses correctly."""
    model.parse("modes([[0, 1], [1, 0]])")
    assert np.all(model.homs == [[0, 1], [1, 0]])
