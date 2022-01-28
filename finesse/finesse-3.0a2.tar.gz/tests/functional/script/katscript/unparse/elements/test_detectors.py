import pytest
from finesse.components import Mirror
from finesse.detectors import PowerDetector
from finesse.script import unparse


# names = pytest.mark.parametrize("name", ("pd1", "pd2", "PD0", "_pd_"))
# nodes = pytest.mark.parametrize("node", ("m1.p1.i", "m1.p1.o", "m1.p2.i", "m1.p2.o"))


@pytest.fixture
def detector_model(model):
    model.add(Mirror("m1"))
    return model


pdtypexfail = pytest.mark.xfail(
    reason="pdtype generation not implemented yet (see #370)"
)


@pytest.mark.parametrize(
    "name,args,kwargs,argument_defaults,prefer_keywords,expected",
    (
        # Optional arguments as positional (note: pdtype is keyword-only).
        ("pd1", ["m1.p1.i"], {}, False, False, "power_detector_dc pd1 m1.p1.i"),
        ("pd1", ["m1.p1.i"], {}, False, True, "power_detector_dc pd1 node=m1.p1.i"),
        (
            "pd1",
            ["m1.p1.i"],
            {},
            True,
            False,
            "power_detector_dc pd1 m1.p1.i pdtype=none",
        ),
        (
            "pd1",
            ["m1.p1.i"],
            {},
            True,
            True,
            "power_detector_dc pd1 node=m1.p1.i pdtype=none",
        ),
        (
            "pd1",
            ["m1.p1.i"],
            {"pdtype": None},
            False,
            False,
            "power_detector_dc pd1 m1.p1.i",
        ),
        (
            "pd1",
            ["m1.p1.i"],
            {"pdtype": None},
            False,
            True,
            "power_detector_dc pd1 node=m1.p1.i",
        ),
        (
            "pd1",
            ["m1.p1.i"],
            {"pdtype": None},
            True,
            False,
            "power_detector_dc pd1 m1.p1.i pdtype=none",
        ),
        (
            "pd1",
            ["m1.p1.i"],
            {"pdtype": None},
            True,
            True,
            "power_detector_dc pd1 node=m1.p1.i pdtype=none",
        ),
        # Optional argument as keyword.
        ("pd1", [], {"node": "m1.p1.i"}, False, False, "power_detector_dc pd1 m1.p1.i"),
        (
            "pd1",
            [],
            {"node": "m1.p1.i"},
            False,
            True,
            "power_detector_dc pd1 node=m1.p1.i",
        ),
        (
            "pd1",
            [],
            {"node": "m1.p1.i"},
            True,
            False,
            "power_detector_dc pd1 m1.p1.i pdtype=none",
        ),
        (
            "pd1",
            [],
            {"node": "m1.p1.i"},
            True,
            True,
            "power_detector_dc pd1 node=m1.p1.i pdtype=none",
        ),
        (
            "pd1",
            [],
            {"node": "m1.p1.i", "pdtype": None},
            False,
            False,
            "power_detector_dc pd1 m1.p1.i",
        ),
        (
            "pd1",
            [],
            {"node": "m1.p1.i", "pdtype": None},
            False,
            True,
            "power_detector_dc pd1 node=m1.p1.i",
        ),
        (
            "pd1",
            [],
            {"node": "m1.p1.i", "pdtype": None},
            True,
            False,
            "power_detector_dc pd1 m1.p1.i pdtype=none",
        ),
        (
            "pd1",
            [],
            {"node": "m1.p1.i", "pdtype": None},
            True,
            True,
            "power_detector_dc pd1 node=m1.p1.i pdtype=none",
        ),
        pytest.param(
            "pd1",
            [],
            {"node": "m1.p1.i", "pdtype": "single"},
            False,
            False,
            "power_detector_dc pd1 m1.p1.i pdtype='single'",
            marks=pdtypexfail,
        ),
        pytest.param(
            "pd1",
            [],
            {"node": "m1.p1.i", "pdtype": "single"},
            False,
            True,
            "power_detector_dc pd1 node=m1.p1.i pdtype='single'",
            marks=pdtypexfail,
        ),
        pytest.param(
            "pd1",
            [],
            {"node": "m1.p1.i", "pdtype": "single"},
            True,
            False,
            "power_detector_dc pd1 m1.p1.i pdtype='single'",
            marks=pdtypexfail,
        ),
        pytest.param(
            "pd1",
            [],
            {"node": "m1.p1.i", "pdtype": "single"},
            True,
            True,
            "power_detector_dc pd1 node=m1.p1.i pdtype='single'",
            marks=pdtypexfail,
        ),
    ),
)
def test_power_detector(
    spec,
    detector_model,
    name,
    args,
    kwargs,
    argument_defaults,
    prefer_keywords,
    expected,
):
    adapter = spec.elements["power_detector_dc"]

    if "node" in kwargs:
        kwargs["node"] = detector_model.get(kwargs["node"])
    else:
        # Assume node is first arg.
        args[0] = detector_model.get(args[0])

    detector_model.add(PowerDetector(name, *args, **kwargs))
    dump = next(iter(adapter.getter(adapter, detector_model)))
    script = unparse(
        dump,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == expected
