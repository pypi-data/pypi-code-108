import pytest
from finesse.components import Mirror
from finesse.analysis.actions import Noxaxis, Xaxis
from finesse.script import unparse


@pytest.fixture
def sweep_model(model):
    model.add(Mirror("m1"))
    return model


@pytest.mark.parametrize(
    "argument_defaults,prefer_keywords,expected",
    (
        (False, False, "noxaxis()"),
        (False, True, "noxaxis()"),
        (True, False, "noxaxis(none, none, 'noxaxis')"),
        (True, True, "noxaxis(pre_step=none, post_step=none, name='noxaxis')"),
    ),
)
def test_noxaxis(spec, sweep_model, argument_defaults, prefer_keywords, expected):
    sweep_model.analysis = Noxaxis()
    adapter = spec.analyses["noxaxis"]
    dump = next(iter(adapter.getter(adapter, sweep_model)))
    script = unparse(
        dump,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == expected


@pytest.mark.parametrize(
    "parameter,mode,start,stop,steps,kwargs,argument_defaults,prefer_keywords,expected",
    (
        # linear, 100 steps from 0 to 1
        ("m1.R", "lin", 0, 1, 100, {}, False, False, "xaxis(m1.R, lin, 0, 1, 100)"),
        (
            "m1.R",
            "lin",
            0,
            1,
            100,
            {},
            False,
            True,
            "xaxis(parameter=m1.R, mode=lin, start=0, stop=1, steps=100)",
        ),
        (
            "m1.R",
            "lin",
            0,
            1,
            100,
            {},
            True,
            False,
            "xaxis(m1.R, lin, 0, 1, 100, false, pre_step=none, post_step=none, name='xaxis')",
        ),
        (
            "m1.R",
            "lin",
            0,
            1,
            100,
            {},
            True,
            True,
            "xaxis(parameter=m1.R, mode=lin, start=0, stop=1, steps=100, relative=false, pre_step=none, post_step=none, name='xaxis')",
        ),
    ),
)
def test_xaxis(
    spec,
    sweep_model,
    parameter,
    mode,
    start,
    stop,
    steps,
    kwargs,
    argument_defaults,
    prefer_keywords,
    expected,
):
    parameter = sweep_model.get(parameter)
    adapter = spec.analyses["xaxis"]
    sweep_model.analysis = Xaxis(parameter, mode, start, stop, steps, **kwargs)
    dump = next(iter(adapter.getter(adapter, sweep_model)))
    script = unparse(
        dump,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == expected
