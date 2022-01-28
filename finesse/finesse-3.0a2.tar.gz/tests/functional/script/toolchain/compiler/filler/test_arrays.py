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
def spec(spec, fake_element_adapter_factory, fake_element_cls):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    return spec


@pytest.mark.parametrize(
    "script,graph_definition",
    (
        # Empty array as positional argument.
        pytest.param(
            "fake_element myelement []",
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
                        extra_tokens "[' ', ' ']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
                        type "ARRAY"
                        extra_tokens "['[', ']']"
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
                ]
                """
            ),
            id="positional-empty-array",
        ),
        # Empty array as keyword argument.
        pytest.param(
            "fake_element myelement a=[]",
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
                        extra_tokens "[' ', ' ']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
                        type "ARRAY"
                        key_token "'a'"
                        extra_tokens "['=', '[', ']']"
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
                ]
                """
            ),
            id="keyword-empty-array",
        ),
        # Non-empty array as positional argument.
        pytest.param(
            "fake_element myelement [1, 2]",
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
                        extra_tokens "[' ', ' ']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
                        type "ARRAY"
                        extra_tokens "['[', ',', ' ', ']']"
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
            id="positional-non-empty-array",
        ),
        # Non-empty array as keyword argument.
        pytest.param(
            "fake_element myelement a=[1, 2]",
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
                        extra_tokens "[' ', ' ']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
                        type "ARRAY"
                        key_token "'a'"
                        extra_tokens "['=', '[', ',', ' ', ']']"
                    ]
                    node [
                        id 3
                        label "kat.0.0.0"
                        type "VALUE"
                        token "'1'"
                    ]
                    node [
                        id 4
                        label "kat.0.0.1"
                        type "VALUE"
                        token "'2'"
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
            id="keyword-non-empty-array",
        ),
    ),
)
def test_arrays(assert_graphs_match, script, graph_definition):
    assert_graphs_match(script, graph_definition)
