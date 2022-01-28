import pytest
from ......util import dedent_multiline


# Override default element to take two arguments.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a, b=None):
            super().__init__(name)
            self.a = a
            self.b = b

    return FakeElement


# Override default analysis to take one argument.
@pytest.fixture
def fake_analysis_cls(fake_analysis_cls):
    class FakeAnalysis(fake_analysis_cls):
        def __init__(self, a):
            self.a = a

    return FakeAnalysis


@pytest.fixture
def spec(
    spec,
    fake_element_adapter_factory,
    fake_element_cls,
    fake_analysis_adapter_factory,
    fake_analysis_cls,
    fake_noop,
):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    spec.register_element(
        fake_element_adapter_factory(
            fake_element_cls, "fake_element_last", factory_kwargs={"last": True}
        )
    )
    spec.register_analysis(fake_analysis_adapter_factory(fake_analysis_cls))
    spec.binary_operators["+"] = fake_noop
    spec.binary_operators["-"] = fake_noop
    spec.unary_operators["-"] = fake_noop
    return spec


@pytest.mark.parametrize(
    "script,expected",
    (
        pytest.param(
            # el2 is a dependency to el1.
            dedent_multiline(
                """
                fake_element el1 &el2.a
                fake_element el2
                """
            ),
            ["kat.1", "kat.0"],
            id="dependency to another element",
        ),
        pytest.param(
            # el1 is a dependency to el2. el2 also contains a self-reference but this edge is not
            # added to the graph and is instead stored separately.
            dedent_multiline(
                """
                fake_element el1 1 2
                fake_element el2 &el1.a 1-&el2.a
                """
            ),
            ["kat.0", "kat.1"],
            id="dependency to another element and self",
        ),
        pytest.param(
            # The nested analysis should not appear in the dependency graph.
            dedent_multiline(
                """
                fake_analysis(fake_analysis())
                """
            ),
            ["kat.0"],
            id="nested dependency",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_analysis(a=-5000+&el1.a)
                fake_element el1 1e5
                """
            ),
            ["kat.1", "kat.0"],
            id="nested expression with dependency",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_element_last el1
                fake_element el2 1e5
                """
            ),
            ["kat.1", "kat.0"],
            id="directive with `build_last` flag",
        ),
    ),
)
def test_build_order(compiler, script, expected):
    compiler.compile(script)
    assert compiler._build_order == expected
