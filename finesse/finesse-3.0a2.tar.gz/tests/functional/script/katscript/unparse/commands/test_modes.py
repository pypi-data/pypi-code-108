import pytest
from finesse.script import unparse


@pytest.mark.parametrize(
    "kwargs,directive_defaults,argument_defaults,prefer_keywords,expected",
    (
        ## modes only
        # empty
        ({}, False, False, False, ""),
        ({}, False, False, True, ""),
        ({}, False, True, False, ""),
        ({}, False, True, True, ""),
        ({}, True, False, False, "modes()"),
        ({}, True, False, True, "modes()"),
        ({}, True, True, False, "modes(off)"),
        ({}, True, True, True, "modes(modes=off)"),
        # string
        ({"modes": "off"}, False, False, False, ""),
        ({"modes": "off"}, False, False, True, ""),
        ({"modes": "off"}, False, True, False, ""),
        ({"modes": "off"}, False, True, True, ""),
        ({"modes": "off"}, True, False, False, "modes()"),
        ({"modes": "off"}, True, False, True, "modes()"),
        ({"modes": "off"}, True, True, False, "modes(off, none, none, none)"),
        (
            {"modes": "off"},
            True,
            True,
            True,
            "modes(modes=off, maxtem=none, include=none, remove=none)",
        ),
        # array
        ({"modes": [[0, 1], [1, 0]]}, False, False, False, "modes([[0, 1], [1, 0]])"),
        (
            {"modes": [[0, 1], [1, 0]]},
            False,
            False,
            True,
            "modes(modes=[[0, 1], [1, 0]])",
        ),
        (
            {"modes": [[0, 1], [1, 0]]},
            False,
            True,
            False,
            "modes([[0, 1], [1, 0]], none, none, none)",
        ),
        (
            {"modes": [[0, 1], [1, 0]]},
            False,
            True,
            True,
            "modes(modes=[[0, 1], [1, 0]], maxtem=none, include=none, remove=none)",
        ),
        ## maxtem only
        ({"maxtem": 2}, False, False, False, "modes(none, 2)"),
        ({"maxtem": 2}, False, False, True, "modes(maxtem=2)"),
        ({"maxtem": 2}, False, True, False, "modes(none, 2, none, none)"),
        (
            {"maxtem": 2},
            False,
            True,
            True,
            "modes(modes=none, maxtem=2, include=none, remove=none)",
        ),
        ## modes and maxtem
        # string mode, numeric maxtem
        ({"modes": "even", "maxtem": 4}, False, False, False, "modes(even, 4)"),
        (
            {"modes": "even", "maxtem": 4},
            False,
            False,
            True,
            "modes(modes=even, maxtem=4)",
        ),
        (
            {"modes": "even", "maxtem": 4},
            False,
            True,
            False,
            "modes(even, 4, none, none)",
        ),
        (
            {"modes": "even", "maxtem": 4},
            False,
            True,
            True,
            "modes(modes=even, maxtem=4, include=none, remove=none)",
        ),
    ),
)
def test_modes(
    spec,
    model,
    kwargs,
    directive_defaults,
    argument_defaults,
    prefer_keywords,
    expected,
):
    adapter = spec.commands["modes"]

    if kwargs:
        adapter.setter(model, ((), kwargs))

    dump = next(iter(adapter.getter(adapter, model)))
    script = unparse(
        dump,
        directive_defaults=directive_defaults,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == expected
