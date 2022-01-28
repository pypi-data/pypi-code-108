import pytest
from finesse.script.exceptions import KatParsingError
from ......util import dedent_multiline, escape_full


# Override default element to take two model parameter arguments.
@pytest.fixture
def fake_element_cls(fake_element_cls, fake_float_parameter):
    @fake_float_parameter("a", "Fake Parameter A")
    @fake_float_parameter("b", "Fake Parameter B")
    class FakeElement(fake_element_cls):
        def __init__(self, name, a=None, b=None):
            super().__init__(name)
            self.a = a
            self.b = b

    return FakeElement


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls, finesse_binop_sub):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    # Have to use real Finesse operator here because the builder matches against Finesse
    # operations.
    spec.binary_operators["-"] = finesse_binop_sub
    return spec


@pytest.mark.parametrize(
    "script,element_def",
    (
        pytest.param(
            "fake_element myelement 1",
            ("myelement", 1),
            id="element-with-arg",
        ),
        pytest.param(
            "fake_element myelement a=1",
            ("myelement", 1),
            id="element-with-kwarg",
        ),
    ),
)
def test_element(model_matcher, fake_element_cls, script, element_def):
    model_matcher(script, [fake_element_cls(*element_def)])


@pytest.mark.parametrize(
    "script,element_defs",
    (
        pytest.param(
            dedent_multiline(
                """
                fake_element myelement1 1
                fake_element myelement2 1-&myelement1.a
                """
            ),
            [("myelement1", 1), ("myelement2", 0)],
        ),
    ),
)
def test_argument_reference(model_matcher, fake_element_cls, script, element_defs):
    model_matcher(script, [fake_element_cls(*defs) for defs in element_defs])


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            "fake_element myelement1 &myelement1.a",
            (
                "\nline 1: cannot set myelement1.a to self-referencing value myelement1.a\n"
                "-->1: fake_element myelement1 &myelement1.a\n"
                "                              ^^^^^^^^^^^^^"
            ),
            id="arg-self-ref",
        ),
        pytest.param(
            "fake_element myelement1 1-&myelement1.a",
            (
                "\nline 1: cannot set myelement1.a to self-referencing value (1-myelement1.a)\n"
                "-->1: fake_element myelement1 1-&myelement1.a\n"
                "                                ^^^^^^^^^^^^^"
            ),
            id="arg-expr-self-ref",
        ),
        pytest.param(
            "fake_element myelement1 a=&myelement1.a",
            (
                "\nline 1: cannot set myelement1.a to self-referencing value myelement1.a\n"
                "-->1: fake_element myelement1 a=&myelement1.a\n"
                "                                ^^^^^^^^^^^^^"
            ),
            id="kwarg-self-ref",
        ),
        pytest.param(
            "fake_element myelement1 a=1-&myelement1.a",
            (
                "\nline 1: cannot set myelement1.a to self-referencing value (1-myelement1.a)\n"
                "-->1: fake_element myelement1 a=1-&myelement1.a\n"
                "                                  ^^^^^^^^^^^^^"
            ),
            id="kwarg-expr-self-ref",
        ),
    ),
)
def test_directly_self_referencing_parameter_invalid(compiler, script, error):
    with pytest.raises(KatParsingError, match=escape_full(error)):
        compiler.compile(script)


@pytest.mark.parametrize(
    "script,element_values",
    (
        pytest.param(
            "fake_element myelement1 1 0.5-&myelement1.a",
            {"a": 1, "b": -0.5},
            id="arg-self-ref-to-arg",
        ),
        pytest.param(
            "fake_element myelement1 1 b=0.5-&myelement1.a",
            {"a": 1, "b": -0.5},
            id="kwarg-self-ref-to-arg",
        ),
        pytest.param(
            "fake_element myelement1 a=1 b=0.5-&myelement1.a",
            {"a": 1, "b": -0.5},
            id="kwarg-self-ref-to-kwarg",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_element myelement1 a=&myelement2.a b=0.5-&myelement1.a
                fake_element myelement2 a=0.5-&myelement2.b b=1
                """
            ),
            {"a": -0.5, "b": 1},
            id="second-order-self-ref",
        ),
    ),
)
def test_same_element_referencing_element(compiler, script, element_values):
    model = compiler.compile(script)
    for key, value in element_values.items():
        assert model.get(f"myelement1.{key}").eval() == value


@pytest.mark.parametrize(
    "script,element_defs",
    (
        pytest.param(
            dedent_multiline(
                """
                fake_element myelement1 1
                fake_element myelement2 2
                fake_element myelement3 3
                """
            ),
            [
                ("myelement1", 1),
                ("myelement2", 2),
                ("myelement3", 3),
            ],
            id="elements",
        ),
    ),
)
def test_script(model_matcher, fake_element_cls, script, element_defs):
    model_matcher(script, [fake_element_cls(*defs) for defs in element_defs])
