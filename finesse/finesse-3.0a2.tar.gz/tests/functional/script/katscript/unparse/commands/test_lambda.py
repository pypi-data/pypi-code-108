import pytest
from finesse.script import unparse


@pytest.mark.parametrize(
    "kwargs,directive_defaults,argument_defaults,prefer_keywords,expected",
    (
        # No lambda command.
        ({}, False, False, False, ""),
        ({}, False, False, True, ""),
        ({}, False, True, False, ""),
        ({}, False, True, True, ""),
        ({}, True, False, False, "lambda()"),
        ({}, True, False, True, "lambda()"),
        ({}, True, True, False, "lambda(1.064e-06)"),
        ({}, True, True, True, "lambda(value=1.064e-06)"),
        # 1550nm.
        ({"value": 1550e-9}, False, False, False, "lambda(1.55e-06)"),
        ({"value": 1550e-9}, False, False, True, "lambda(value=1.55e-06)"),
        ({"value": 1550e-9}, False, True, False, "lambda(1.55e-06)"),
        ({"value": 1550e-9}, False, True, True, "lambda(value=1.55e-06)"),
    ),
)
def test_lambda(
    spec,
    model,
    kwargs,
    directive_defaults,
    argument_defaults,
    prefer_keywords,
    expected,
):
    adapter = spec.commands["lambda"]

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
