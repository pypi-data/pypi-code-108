import pytest
from finesse.symbols import OPERATORS, FUNCTIONS


# Override default element to take two arguments.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a=None, b=None):
            super().__init__(name)
            self.a = a
            self.b = b

    return FakeElement


@pytest.fixture
def fake_variadic_element_cls(fake_element_cls):
    class FakeVariadicElement(fake_element_cls):
        def __init__(self, name, a, *args, b=None, **kwargs):
            super().__init__(name)
            self.a = a
            self.args = args
            self.b = b
            self.kwargs = kwargs

    return FakeVariadicElement


@pytest.fixture
def spec(
    spec, fake_element_adapter_factory, fake_element_cls, fake_variadic_element_cls
):
    spec.register_element(
        fake_element_adapter_factory(
            fake_element_cls, full_name="fake_element", short_name="fake"
        )
    )
    spec.register_element(
        fake_element_adapter_factory(
            fake_variadic_element_cls,
            full_name="fake_variadic_element",
            short_name="fake_var",
        )
    )
    spec.unary_operators["-"] = FUNCTIONS["neg"]
    spec.binary_operators["+"] = OPERATORS["__add__"]
    spec.expression_functions["cos"] = FUNCTIONS["cos"]
    return spec


@pytest.mark.parametrize("katdelim", (" ", "  ", "   "))
@pytest.mark.parametrize(
    "katargs,katkwargs",
    (
        ([], {}),
        ([""], {}),
        ([" "], {}),
        (["   "], {}),
        (["none"], {}),
        (["none", "none"], {}),
        (["none"], {"b": "none"}),
        ([], {"a": "none", "b": "none"}),
        (["1.23"], {}),
        (["1.23", "4.56"], {}),
        (["1.23"], {"b": "4.56"}),
        ([], {"a": "1.23", "b": "4.56"}),
    ),
)
def test_element(compiler, regenerate, katdelim, katargs, katkwargs):
    args = " ".join(katargs)
    kwargs = " ".join([f"{k}={v}" for k, v in katkwargs.items()])
    script = f"fake_element{katdelim}myelement{katdelim}{args}{katdelim}{kwargs}"
    model = compiler.compile(script)
    assert regenerate(model) == script
