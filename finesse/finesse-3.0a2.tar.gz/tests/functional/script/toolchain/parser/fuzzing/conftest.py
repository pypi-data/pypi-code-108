import math
import cmath
import pytest
from finesse.components.general import Connector
from finesse.script.adapter import ItemAdapter
from finesse.script.spec import KatSpec, ElementFactory, ElementSetter
from finesse.script.compiler import KatCompiler


def resolve(value):
    if isinstance(value, list):
        for index, item in enumerate(value):
            value[index] = resolve(item)
    else:
        try:
            value = value.eval()
        except AttributeError:
            pass

    return value


@pytest.fixture(scope="package")
def fuzz_value_parse_compare():
    """Special package-scoped parser for fuzzing values."""

    class FakeNoParamElement(Connector):
        """A fake element with no model parameters."""

        def __init__(self, name, a=None):
            super().__init__(name)
            self.a = a

    # Register special fuzz component.
    spec = KatSpec()
    spec.register_element(
        ItemAdapter(
            "fuzz",
            factory=ElementFactory(item_type=FakeNoParamElement),
            setter=ElementSetter(item_type=FakeNoParamElement),
        )
    )
    compiler = KatCompiler(spec=spec)

    def _(value, expected, exact=True):
        model = compiler.compile(f"fuzz fuzzer {value}")
        value = resolve(model.fuzzer.a)
        expected = resolve(expected)

        # Some special conditions first.
        if (
            isinstance(value, complex)
            and isinstance(expected, complex)
            and cmath.isnan(value)
            and cmath.isnan(expected)
        ):
            # Both nan.
            return
        if (
            isinstance(value, float)
            and isinstance(expected, float)
            and math.isnan(value)
            and math.isnan(expected)
        ):
            # Both nan.
            return

        if exact:
            assert value == expected
        else:
            assert value == pytest.approx(expected)

    return _
