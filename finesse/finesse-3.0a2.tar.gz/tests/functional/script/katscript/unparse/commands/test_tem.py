import pytest
from finesse.components.laser import Laser
from finesse.script import unparse


@pytest.fixture
def laser_model(model):
    model.add(Laser("l1"))
    return model


@pytest.mark.parametrize(
    "kwargs,directive_defaults,argument_defaults,prefer_keywords,expected",
    (
        ## No TEM commands.
        (None, False, False, False, ""),
        (None, False, False, True, ""),
        (None, False, True, False, ""),
        (None, False, True, True, ""),
        (None, True, False, False, "tem(l1, 0, 0, 1.0)"),
        (None, True, False, True, "tem(laser=l1, n=0, m=0, factor=1.0)"),
        (None, True, True, False, "tem(l1, 0, 0, 1.0, 0.0)"),
        (None, True, True, True, "tem(laser=l1, n=0, m=0, factor=1.0, phase=0.0)"),
        ## Non-empty commands.
        # No phase.
        ({"n": 0, "m": 0, "factor": 0.5}, False, False, False, "tem(l1, 0, 0, 0.5)"),
        (
            {"n": 0, "m": 0, "factor": 0.5},
            False,
            False,
            True,
            "tem(laser=l1, n=0, m=0, factor=0.5)",
        ),
        (
            {"n": 0, "m": 0, "factor": 0.5},
            False,
            True,
            False,
            "tem(l1, 0, 0, 0.5, 0.0)",
        ),
        (
            {"n": 0, "m": 0, "factor": 0.5},
            False,
            True,
            True,
            "tem(laser=l1, n=0, m=0, factor=0.5, phase=0.0)",
        ),
        # Phase set to default.
        (
            {"n": 0, "m": 0, "factor": 0.5, "phase": 0.0},
            False,
            False,
            False,
            "tem(l1, 0, 0, 0.5)",
        ),
        (
            {"n": 0, "m": 0, "factor": 0.5, "phase": 0.0},
            False,
            False,
            True,
            "tem(laser=l1, n=0, m=0, factor=0.5)",
        ),
        (
            {"n": 0, "m": 0, "factor": 0.5, "phase": 0.0},
            False,
            True,
            False,
            "tem(l1, 0, 0, 0.5, 0.0)",
        ),
        (
            {"n": 0, "m": 0, "factor": 0.5, "phase": 0.0},
            False,
            True,
            True,
            "tem(laser=l1, n=0, m=0, factor=0.5, phase=0.0)",
        ),
        # Phase not set to default.
        (
            {"n": 0, "m": 0, "factor": 0.5, "phase": 45},
            False,
            False,
            False,
            "tem(l1, 0, 0, 0.5, 45.0)",
        ),
        (
            {"n": 0, "m": 0, "factor": 0.5, "phase": 45},
            False,
            False,
            True,
            "tem(laser=l1, n=0, m=0, factor=0.5, phase=45.0)",
        ),
        (
            {"n": 0, "m": 0, "factor": 0.5, "phase": 45.0},
            False,
            True,
            False,
            "tem(l1, 0, 0, 0.5, 45.0)",
        ),
        (
            {"n": 0, "m": 0, "factor": 0.5, "phase": 45.0},
            False,
            True,
            True,
            "tem(laser=l1, n=0, m=0, factor=0.5, phase=45.0)",
        ),
    ),
)
def test_tem(
    spec,
    laser_model,
    kwargs,
    directive_defaults,
    argument_defaults,
    prefer_keywords,
    expected,
):
    adapter = spec.commands["tem"]

    if kwargs:
        laser_model.l1.tem(**kwargs)

    dump = next(iter(adapter.getter(adapter, laser_model)))
    script = unparse(
        dump,
        directive_defaults=directive_defaults,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == expected
