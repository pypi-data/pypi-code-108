import pytest
from finesse.components import Modulator
from finesse.script import unparse


# names = pytest.mark.parametrize("name", ("mod", "mod1"))
# frequencies = pytest.mark.parametrize("f", (1e6, 8.5e6))
# indices = pytest.mark.parametrize("midx", (0.1, 0.3))
# orders_and_types = pytest.mark.parametrize(
#     "mod_type,order",
#     (
#         # AM only works with order 1.
#         (ModulatorType.am, 1),
#         (ModulatorType.pm, 1),
#         (ModulatorType.pm, 2),
#         (ModulatorType.pm, 3),
#     ),
# )
# phases = pytest.mark.parametrize("phase", (0.0, 90.0))  # Floats!
# positive_only = pytest.mark.parametrize("positive_only", (True, False))


@pytest.mark.parametrize(
    "f,midx,kwargs,argument_defaults,prefer_keywords,expected",
    (
        (1e6, 0.1, {}, False, False, "modulator mod1 1000000.0 0.1"),
        (1e6, 0.1, {}, False, True, "modulator mod1 f=1000000.0 midx=0.1"),
        (1e6, 0.1, {}, True, False, "modulator mod1 1000000.0 0.1 1 pm 0.0 false"),
        (
            1e6,
            0.1,
            {},
            True,
            True,
            "modulator mod1 f=1000000.0 midx=0.1 order=1 mod_type=pm phase=0.0 positive_only=false",
        ),
        (
            1e3,
            0.3,
            {"order": 2, "positive_only": True},
            False,
            False,
            "modulator mod1 1000.0 0.3 2 pm 0.0 true",
        ),
        (
            1e3,
            0.3,
            {"order": 2, "positive_only": True},
            False,
            True,
            "modulator mod1 f=1000.0 midx=0.3 order=2 positive_only=true",
        ),
        (
            1e3,
            0.3,
            {"order": 2, "positive_only": True},
            True,
            False,
            "modulator mod1 1000.0 0.3 2 pm 0.0 true",
        ),
        (
            1e3,
            0.3,
            {"order": 2, "positive_only": True},
            True,
            True,
            "modulator mod1 f=1000.0 midx=0.3 order=2 mod_type=pm phase=0.0 positive_only=true",
        ),
    ),
)
def test_modulator(
    spec, model, f, midx, kwargs, argument_defaults, prefer_keywords, expected
):
    adapter = spec.elements["modulator"]
    model.add(Modulator("mod1", f=f, midx=midx, **kwargs))
    dump = next(iter(adapter.getter(adapter, model)))
    script = unparse(
        dump,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == expected
