"""Kat compiler toolchain value tests.

Note: it is preferable to test compiled kat script values in the `katparser` testing module since
this tests the end-user language constructs directly. In some cases it's however not easy to test a
particular aspect with the available kat script elements, commands, etc. and instead custom
constructs are required; in such cases the tests should go here.
"""

import pytest
import numpy as np
from finesse.parameter import float_parameter
from finesse.symbols import Constant
from ......util import dedent_multiline


# Override default element to take one model parameter argument.
# Use different name to fake_element_cls to avoid overwriting the dependency for
# fake_element_noparam_cls below.
@pytest.fixture
def fake_element_std_cls(fake_element_cls):
    @float_parameter("a", "Fake Parameter A")
    class FakeElement(fake_element_cls):
        def __init__(self, name, a):
            super().__init__(name)
            self.a = a

    return FakeElement


# Fake element without model parameters.
@pytest.fixture
def fake_element_noparam_cls(fake_element_cls):
    class FakeElementNoParam(fake_element_cls):
        def __init__(self, name, a):
            super().__init__(name)
            self.a = a

    return FakeElementNoParam


@pytest.fixture
def spec(
    spec,
    fake_element_adapter_factory,
    fake_element_std_cls,
    fake_element_noparam_cls,
    finesse_binop_mul,
    finesse_unop_neg,
):
    spec.register_element(
        fake_element_adapter_factory(fake_element_std_cls, "fake_element")
    )
    spec.register_element(
        fake_element_adapter_factory(fake_element_noparam_cls, "fake_element_noparam")
    )
    # Have to use real Finesse operator here because the builder matches against Finesse
    # operations.
    spec.binary_operators["*"] = finesse_binop_mul
    spec.unary_operators["-"] = finesse_unop_neg
    return spec


@pytest.mark.parametrize(
    "expression,expected",
    (
        ("2*[1, 2]", 2 * np.array([1, 2])),
        ("3.141*[1, 2, 3, 4, 5]", 3.141 * np.array([1, 2, 3, 4, 5])),
        ("-10*[[1], [2], [3]]", -10 * np.array([[1], [2], [3]])),
    ),
)
def test_eager_numerical_array(compiler, expression, expected):
    # NOTE: this uses a fake element with no model parameters because model parameters
    # don't support ndarray values.
    model = compiler.compile(f"fake_element_noparam myel1 {expression}")
    np.testing.assert_array_equal(model.myel1.a, expected)


def test_lazy_numerical_array(compiler, finesse_binop_mul):
    """Test reference inside array.

    These are lazily evaluated because they contain symbols.
    """
    model = compiler.compile(
        dedent_multiline(
            """
            fake_element myel1 a=1
            fake_element_noparam myel2 -2*[1, &myel1.a]
            """
        )
    )
    np.testing.assert_array_equal(
        model.myel2.a.eval(),
        np.array([-2, finesse_binop_mul(Constant(-2), model.myel1.a.ref)]),
    )
