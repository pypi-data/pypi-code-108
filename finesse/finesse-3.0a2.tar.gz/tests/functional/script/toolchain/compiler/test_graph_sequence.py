"""Test the sequence number defined for each parse call.

A sequence number is created for each parse call, and parsed items are joined to the
root node in the syntax graph by an edge with order attribute set to this number. This
allows the model elements to be later re-sorted into script order even though the parser
does not build elements into the model in that order.
"""

import pytest
from ....diff import assert_graph_matches_def


# Override default element to take two arguments.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a, b=None):
            super().__init__(name)
            self.a = a
            self.b = b

    return FakeElement


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    return spec


def test_multiple_parses_have_different_sequences(compiler, model):
    """Test that parsing KatScript into the same model multiple times results in
    different branches in the syntax graph."""
    # Graph after first parse.
    refgraph1 = """
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
                name_token "'myelement1'"
                extra_tokens "[' ', ' ']"
            ]
            node [
                id 2
                label "kat.0.0"
                type "VALUE"
                token "'1'"
                key_token "'a'"
                extra_tokens "['=']"
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
    compiler.compile("fake_element myelement1 a=1", model=model)
    assert_graph_matches_def(model.syntax_graph, refgraph1)

    # Graph after second parse.
    refgraph2 = """
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
                name_token "'myelement1'"
                extra_tokens "[' ', ' ']"
            ]
            node [
                id 2
                label "kat.0.0"
                type "VALUE"
                token "'1'"
                key_token "'a'"
                extra_tokens "['=']"
            ]
            node [
                id 3
                label "kat.1"
                type "ELEMENT"
                token "'fake_element'"
                name_token "'myelement2'"
                extra_tokens "[' ', ' ', ' ']"
            ]
            node [
                id 4
                label "kat.1.0"
                type "VALUE"
                token "'2'"
                key_token "'a'"
                extra_tokens "['=']"
            ]
            node [
                id 5
                label "kat.1.1"
                type "VALUE"
                token "'3'"
                key_token "'b'"
                extra_tokens "['=']"
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
                target 0
                type "ARGUMENT"
                order "1"
            ]
            edge [
                source 4
                target 3
                type "ARGUMENT"
                order "0"
            ]
            edge [
                source 5
                target 3
                type "ARGUMENT"
                order "1"
            ]
        ]
        """
    compiler.compile("fake_element myelement2 a=2 b=3", model=model)
    assert_graph_matches_def(model.syntax_graph, refgraph2)
