import pytest
from ......util import dedent_multiline


# Override default element to take one model parameter argument.
@pytest.fixture
def fake_element_cls(fake_element_cls, fake_float_parameter):
    @fake_float_parameter("a", "Fake Parameter A")
    class FakeElement(fake_element_cls):
        def __init__(self, name, a=None):
            super().__init__(name)
            self.a = a

    return FakeElement


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    spec.constants = {"A": 1, "B": "2", "C": object, "D": lambda: "hi"}
    spec.keywords = {"E", "F", "G", "H"}
    return spec


@pytest.mark.parametrize(
    "script,graph_definition",
    (
        pytest.param(
            dedent_multiline(
                """
                fake_element myelement1
                fake_element myelement2 myelement1.a
                """
            ),
            dedent_multiline(
                """
                graph [
                    directed 1
                    node [
                        id 0
                        label "kat"
                        type "ROOT"
                        extra_tokens "['\\n']"
                    ]
                    node [
                        id 1
                        label "kat.0"
                        type "ELEMENT"
                        token "'fake_element'"
                        name_token "'myelement1'"
                        extra_tokens "[' ']"
                    ]
                    node [
                        id 2
                        label "kat.1"
                        type "ELEMENT"
                        token "'fake_element'"
                        name_token "'myelement2'"
                        extra_tokens "[' ', ' ']"
                    ]
                    node [
                        id 3
                        label "kat.1.0"
                        token "'myelement1.a'"
                        type "PARAMETER"
                    ]
                    edge [
                        source 1
                        target 0
                        type "ARGUMENT"
                        order "0"
                    ]
                    edge [
                        source 2
                        target 0
                        type "ARGUMENT"
                        order "1"
                    ]
                    edge [
                        source 3
                        target 2
                        type "ARGUMENT"
                        order "0"
                    ]
                    edge [
                        source 1
                        target 3
                        type "DEPENDENCY"
                    ]
                ]
                """
            ),
            id="parameter between two elements",
        ),
    ),
)
def test_parameter(assert_graphs_match, script, graph_definition):
    assert_graphs_match(script, graph_definition)


@pytest.mark.parametrize(
    "script,graph_definition",
    (
        pytest.param(
            dedent_multiline(
                """
                fake_element myelement1
                fake_element myelement2 &myelement1.a
                """
            ),
            dedent_multiline(
                """
                graph [
                    directed 1
                    node [
                        id 0
                        label "kat"
                        type "ROOT"
                        extra_tokens "['\\n']"
                    ]
                    node [
                        id 1
                        label "kat.0"
                        type "ELEMENT"
                        token "'fake_element'"
                        name_token "'myelement1'"
                        extra_tokens "[' ']"
                    ]
                    node [
                        id 2
                        label "kat.1"
                        type "ELEMENT"
                        token "'fake_element'"
                        name_token "'myelement2'"
                        extra_tokens "[' ', ' ']"
                    ]
                    node [
                        id 3
                        label "kat.1.0"
                        token "'&myelement1.a'"
                        type "PARAMETER_REFERENCE"
                    ]
                    edge [
                        source 1
                        target 0
                        type "ARGUMENT"
                        order "0"
                    ]
                    edge [
                        source 2
                        target 0
                        type "ARGUMENT"
                        order "1"
                    ]
                    edge [
                        source 3
                        target 2
                        type "ARGUMENT"
                        order "0"
                    ]
                    edge [
                        source 1
                        target 3
                        type "DEPENDENCY"
                    ]
                ]
                """
            ),
            id="parameter reference between two elements",
        ),
    ),
)
def test_parameter_reference(assert_graphs_match, script, graph_definition):
    assert_graphs_match(script, graph_definition)
