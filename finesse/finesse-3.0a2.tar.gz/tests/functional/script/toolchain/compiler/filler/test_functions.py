import pytest
from ......util import dedent_multiline


# Override default command to take two optional arguments.
@pytest.fixture
def fake_command_func():
    def fake_command(model, a=None, b=None):
        pass

    return fake_command


@pytest.fixture
def spec(spec, fake_command_adapter_factory, fake_command_func):
    spec.register_command(fake_command_adapter_factory(fake_command_func))
    return spec


@pytest.mark.parametrize(
    "script,graph_definition",
    (
        pytest.param(
            "fake_command()",
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
                        token "'fake_command'"
                        type "FUNCTION"
                        extra_tokens "['(', ')']"
                    ]
                    edge [
                        source 1
                        target 0
                        type "ARGUMENT"
                        order "0"
                    ]
                ]
                """
            ),
            id="function with no arguments",
        ),
        pytest.param(
            "fake_command(1)",
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
                        token "'fake_command'"
                        type "FUNCTION"
                        extra_tokens "['(', ')']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
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
                ]
                """
            ),
            id="function with 1 argument",
        ),
        pytest.param(
            "fake_command(1, 2)",
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
                        token "'fake_command'"
                        type "FUNCTION"
                        extra_tokens "['(', ',', ' ', ')']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
                        token "'1'"
                        type "VALUE"
                    ]
                    node [
                        id 3
                        label "kat.0.1"
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
                        target 1
                        type "ARGUMENT"
                        order "1"
                    ]
                ]
                """
            ),
            id="function with 2 arguments",
        ),
        pytest.param(
            "fake_command(fake_command(3))",
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
                        token "'fake_command'"
                        type "FUNCTION"
                        extra_tokens "['(', ')']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
                        token "'fake_command'"
                        type "FUNCTION"
                        extra_tokens "['(', ')']"
                    ]
                    node [
                        id 3
                        label "kat.0.0.0"
                        token "'3'"
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
                """,
            ),
            id="function with nested function argument",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_command(
                    fake_command(3)
                )
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
                        extra_tokens "[]"
                    ]
                    node [
                        id 1
                        label "kat.0"
                        token "'fake_command'"
                        type "FUNCTION"
                        extra_tokens "['(', '\\n', '    ', '\\n', ')']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
                        token "'fake_command'"
                        type "FUNCTION"
                        extra_tokens "['(', ')']"
                    ]
                    node [
                        id 3
                        label "kat.0.0.0"
                        token "'3'"
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
                """,
            ),
            id="function with nested function argument across multiple lines",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_command(1)
                fake_command(2)
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
                        token "'fake_command'"
                        type "FUNCTION"
                        extra_tokens "['(', ')']"
                    ]
                    node [
                        id 2
                        label "kat.0.0"
                        token "'1'"
                        type "VALUE"
                    ]
                    node [
                        id 3
                        label "kat.1"
                        token "'fake_command'"
                        type "FUNCTION"
                        extra_tokens "['(', ')']"
                    ]
                    node [
                        id 4
                        label "kat.1.0"
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
                ]
                """
            ),
            id="multiple functions",
        ),
    ),
)
def test_function(assert_graphs_match, script, graph_definition):
    assert_graphs_match(script, graph_definition)
