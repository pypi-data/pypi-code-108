import pytest
from ......util import dedent_multiline


# Override default element to take one argument.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a):
            super().__init__(name)
            self.a = a

    return FakeElement


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls, fake_noop):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    spec.binary_operators["+"] = fake_noop
    return spec


@pytest.mark.parametrize(
    "script,graph_definition",
    (
        pytest.param(
            "fake_element el1 1+2",
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
                        token "'fake_element'"
                        name_token "'el1'"
                        type "ELEMENT"
                        extra_tokens "[' ', ' ']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
                        token "'+'"
                        type "EXPRESSION"
                    ]
                    node [
                        id 3
                        label "kat.0.0.0"
                        token "'1'"
                        type "VALUE"
                    ]
                    node [
                        id 4
                        label "kat.0.0.1"
                        token "'2'"
                        type "VALUE"
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
                        target 2
                        type "ARGUMENT"
                        order "0"
                    ]
                    edge [
                        source 4
                        target 2
                        type "ARGUMENT"
                        order "1"
                    ]
                ]
                """
            ),
            id="1+2",
        ),
        pytest.param(
            "fake_element el1 (1)",
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
                        token "'fake_element'"
                        name_token "'el1'"
                        type "ELEMENT"
                        extra_tokens "[' ', ' ']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
                        type "GROUPED_EXPRESSION"
                        extra_tokens "['(', ')']"
                    ]
                    node [
                        id 3
                        label "kat.0.0.0"
                        token "'1'"
                        type "VALUE"
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
                        target 2
                        type "ARGUMENT"
                        order "0"
                    ]
                ]
                """
            ),
            id="grouped expression",
        ),
    ),
)
def test_expression(assert_graphs_match, script, graph_definition):
    assert_graphs_match(script, graph_definition)
