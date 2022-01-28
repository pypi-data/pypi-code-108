"""Test parameter errors."""

import pytest
from finesse.components import Laser, Mirror, Space
from finesse.detectors import PowerDetector
from finesse.exceptions import (
    ContextualTypeError,
    ContextualValueError,
)
from ..util import escape_full


def test_type_error(model):
    """Incorrect parameter types should raise an error that offers allowed types."""
    laser = Laser("l1")

    with pytest.raises(
        ContextualTypeError,
        match=escape_full("\nnode: invalid type (expected 'Node', got 'Laser')"),
    ):
        model.add(PowerDetector("pd", laser))


def test_value_error(model):
    laser = Laser("l1")
    mirror = Mirror("m1")

    with pytest.raises(
        ContextualValueError,
        match=(
            r"\n'portB': invalid value \<Port m1.mech Type=NodeType.MECHANICAL @ "
            r"(.*)\> \(must be an optical port\)"
        ),
    ):
        model.add(laser)
        model.add(mirror)
        model.add(Space("s1", portA=laser.p1, portB=mirror.mech))

# changed the behaviour when renaming select_modes to modes
@pytest.mark.xfail
def test_multi_value_error(model):
    with pytest.raises(
        ContextualValueError,
        match=escape_full(
            "\n'select' and 'maxtem': invalid values (cannot both be empty)"
        ),
    ):
        model.modes()
