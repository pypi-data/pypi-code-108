import pytest
from ......util import dedent_multiline


# Override default element to take four arguments.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a, b, c, d):
            super().__init__(name)
            self.a = a
            self.b = b
            self.c = c
            self.d = d

    return FakeElement


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    spec.constants = {"A": 1, "B": 2, "C": 3, "D": 4}
    return spec


@pytest.mark.parametrize(
    "script,graph_definition",
    (
        pytest.param(
            "fake_element myelement A B C D",
            dedent_multiline(
                """
                graph [
                    directed 1
                    node [
                        id 0
                        label "kat"
                        type "ROOT"
                        extra_tokens "[]"
                    ]
                    node [
                        id 1
                        label "kat.0"
                        type "ELEMENT"
                        token "'fake_element'"
                        name_token "'myelement'"
                        extra_tokens "[' ', ' ', ' ', ' ', ' ']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
                        token "'A'"
                        type "CONSTANT"
                    ]
                    node [
                        id 3
                        label "kat.0.1"
                        token "'B'"
                        type "CONSTANT"
                    ]
                    node [
                        id 4
                        label "kat.0.2"
                        token "'C'"
                        type "CONSTANT"
                    ]
                    node [
                        id 5
                        label "kat.0.3"
                        token "'D'"
                        type "CONSTANT"
                    ]
                    edge [
                        source 1
                        target 0
                        type "ARGUMENT"
                        order "0"
                    ]
                    edge [
                        source 2
                        target 1
                        type "ARGUMENT"
                        order "0"
                    ]
                    edge [
                        source 3
                        target 1
                        type "ARGUMENT"
                        order "1"
                    ]
                    edge [
                        source 4
                        target 1
                        type "ARGUMENT"
                        order "2"
                    ]
                    edge [
                        source 5
                        target 1
                        type "ARGUMENT"
                        order "3"
                    ]
                ]
                """
            ),
            id="element with 4 constants",
        ),
    ),
)
def test_constants(assert_graphs_match, script, graph_definition):
    assert_graphs_match(script, graph_definition)
