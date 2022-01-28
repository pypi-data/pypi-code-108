import pytest
from finesse.components import Mirror, ReadoutRF
from finesse.locks import Lock
from finesse.script import unparse


@pytest.fixture
def lock_model(model):
    model.add(Mirror("m1"))
    model.add(ReadoutRF("pdh1", model.m1.p1.o, f=10e6))
    return model


@pytest.mark.parametrize(
    "name,args,kwargs,argument_defaults,prefer_keywords,expected",
    (
        # Optional arguments as positional (note: disabled and offset are keyword-only).
        (
            "lock1",
            ["pdh1.outputs.I", "m1.Rcx", 1, 1e-9],
            {},
            False,
            False,
            "lock lock1 pdh1_I m1.Rcx 1 1e-09",
        ),
        (
            "lock1",
            ["pdh1.outputs.I", "m1.Rcx", 1, 1e-9],
            {},
            False,
            True,
            "lock lock1 error_signal=pdh1_I feedback=m1.Rcx gain=1 accuracy=1e-09",
        ),
        (
            "lock1",
            ["pdh1.outputs.I", "m1.Rcx", 1, 1e-9],
            {},
            True,
            False,
            "lock lock1 pdh1_I m1.Rcx 1 1e-09 disabled=false offset=0",
        ),
        (
            "lock1",
            ["pdh1.outputs.I", "m1.Rcx", 1, 1e-9],
            {},
            True,
            True,
            "lock lock1 error_signal=pdh1_I feedback=m1.Rcx gain=1 accuracy=1e-09 disabled=false offset=0",
        ),
        # Optional argument as keyword.
        (
            "lock1",
            [],
            {
                "error_signal": "pdh1.outputs.I",
                "feedback": "m1.Rcx",
                "gain": 1,
                "accuracy": 1e-9,
                "disabled": False,
                "offset": 0,
            },
            False,
            False,
            "lock lock1 pdh1_I m1.Rcx 1 1e-09",
        ),
        (
            "lock1",
            [],
            {
                "error_signal": "pdh1.outputs.I",
                "feedback": "m1.Rcx",
                "gain": 1,
                "accuracy": 1e-9,
                "disabled": False,
                "offset": 0,
            },
            False,
            True,
            "lock lock1 error_signal=pdh1_I feedback=m1.Rcx gain=1 accuracy=1e-09",
        ),
        (
            "lock1",
            [],
            {
                "error_signal": "pdh1.outputs.I",
                "feedback": "m1.Rcx",
                "gain": 1,
                "accuracy": 1e-9,
                "disabled": False,
                "offset": 0,
            },
            True,
            False,
            "lock lock1 pdh1_I m1.Rcx 1 1e-09 disabled=false offset=0",
        ),
        (
            "lock1",
            [],
            {
                "error_signal": "pdh1.outputs.I",
                "feedback": "m1.Rcx",
                "gain": 1,
                "accuracy": 1e-9,
                "disabled": False,
                "offset": 0,
            },
            True,
            True,
            "lock lock1 error_signal=pdh1_I feedback=m1.Rcx gain=1 accuracy=1e-09 disabled=false offset=0",
        ),
    ),
)
def test_lock(
    spec,
    lock_model,
    name,
    args,
    kwargs,
    argument_defaults,
    prefer_keywords,
    expected,
):
    if "error_signal" in kwargs:
        kwargs["error_signal"] = lock_model.get(kwargs["error_signal"])
    else:
        # Assume error_signal is first arg.
        args[0] = lock_model.get(args[0])

    if "feedback" in kwargs:
        kwargs["feedback"] = lock_model.get(kwargs["feedback"])
    else:
        # Assume feedback is second arg.
        args[1] = lock_model.get(args[1])

    adapter = spec.elements["lock"]
    lock_model.add(Lock(name, *args, **kwargs))
    dump = next(iter(adapter.getter(adapter, lock_model)))
    script = unparse(
        dump,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == expected
