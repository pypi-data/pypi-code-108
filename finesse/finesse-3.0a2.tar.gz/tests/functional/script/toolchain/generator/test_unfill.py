import pytest
from finesse.script.graph import KatNodeType, KatEdgeType
from ..util import (
    NAME,
    NUMBER,
    EQUALS,
    COMMA,
    SPACE,
    LPAREN,
    RPAREN,
    LBRACKET,
    RBRACKET,
)


token_value_parameters = pytest.mark.parametrize(
    "token",
    (
        # Numbers.
        NUMBER(1, 1, "1"),
        # Parameters.
        NAME(1, 1, "m1.T"),
        NAME(1, 1, "&m1.T"),
        # Constants.
        NAME(1, 1, "A"),
        # Keywords.
        NAME(1, 1, "lin"),
    ),
)


@token_value_parameters
def test_value(unfiller, graph, token):
    """Single values."""
    graph.add_node("myval", token=token, type=KatNodeType.VALUE)
    assert unfiller.unfill("myval", graph) == token.raw_value


@pytest.mark.parametrize(
    "key_token,equals_token,value_token",
    (
        # Numbers.
        (NAME(1, 1, "a"), EQUALS(1, 2), NUMBER(1, 3, "1")),
        # Parameters.
        (NAME(1, 1, "a"), EQUALS(1, 2), NAME(1, 3, "m1.T")),
        (NAME(1, 1, "a"), EQUALS(1, 2), NAME(1, 3, "&m1.T")),
        # Constants.
        (NAME(1, 1, "a"), EQUALS(1, 2), NAME(1, 3, "A")),
        # Keywords.
        (NAME(1, 1, "a"), EQUALS(1, 2), NAME(1, 3, "lin")),
    ),
)
def test_kwarg(unfiller, graph, key_token, equals_token, value_token):
    """Keyword values in arguments."""
    graph.add_node(
        "myarg",
        type=KatNodeType.VALUE,
        token=value_token,
        key_token=key_token,
        extra_tokens=[equals_token],
    )
    expected = "".join(
        [tok.raw_value for tok in (key_token, equals_token, value_token)]
    )
    assert unfiller.unfill("myarg", graph) == expected


@pytest.mark.parametrize(
    "operator,arguments,extra,expected",
    (
        pytest.param(
            NAME(1, 2, "+"),
            [NUMBER(1, 1, "1"), NUMBER(1, 3, "2")],
            [],
            "1+2",
            id="1+2",
        ),
    ),
)
def test_expression(unfiller, graph, operator, arguments, extra, expected):
    expression_node = "myexpr"
    graph.add_node(
        expression_node, token=operator, type=KatNodeType.EXPRESSION, extra_tokens=extra
    )
    for order, argument in enumerate(arguments):
        arg_node = f"{expression_node}.{order}"
        graph.add_node(arg_node, token=argument, type=KatNodeType.VALUE)
        graph.add_edge(
            arg_node, expression_node, type=KatEdgeType.ARGUMENT, order=order
        )

    assert unfiller.unfill(expression_node, graph) == expected


@pytest.mark.parametrize(
    "function,arguments,extra,expected",
    (
        pytest.param(
            NAME(1, 1, "cos"),
            [NUMBER(1, 5, "1")],
            [LPAREN(1, 4), RPAREN(1, 6)],
            "cos(1)",
            id="cos(1)",
        ),
        pytest.param(
            NAME(1, 1, "cos"),
            [NUMBER(1, 5, "1"), NUMBER(1, 8, "2")],
            [LPAREN(1, 4), COMMA(1, 6), RPAREN(1, 9)],
            "cos(1,2)",
            id="cos(1,2)",
        ),
        pytest.param(
            NAME(1, 1, "cos"),
            [NUMBER(1, 5, "1"), NUMBER(1, 8, "2")],
            [LPAREN(1, 4), COMMA(1, 6), SPACE(1, 7), RPAREN(1, 9)],
            "cos(1, 2)",
            id="cos(1, 2)",
        ),
    ),
)
def test_expression_function(unfiller, graph, function, arguments, extra, expected):
    function_node = "myfunc"
    graph.add_node(
        function_node, token=function, type=KatNodeType.FUNCTION, extra_tokens=extra
    )
    for order, argument in enumerate(arguments):
        arg_node = f"{function_node}.{order}"
        graph.add_node(arg_node, token=argument, type=KatNodeType.VALUE)
        graph.add_edge(arg_node, function_node, type=KatEdgeType.ARGUMENT, order=order)

    assert unfiller.unfill(function_node, graph) == expected


@pytest.mark.parametrize(
    "arguments,extra,expected",
    (
        pytest.param(
            [NUMBER(1, 2, "1")], [LPAREN(1, 1), RPAREN(1, 3)], "(1)", id="(1)",
        ),
    ),
)
def test_grouped_expression(unfiller, graph, arguments, extra, expected):
    group_node = "mygroup"
    graph.add_node(group_node, type=KatNodeType.GROUPED_EXPRESSION, extra_tokens=extra)
    for order, argument in enumerate(arguments):
        arg_node = f"{group_node}.{order}"
        graph.add_node(arg_node, token=argument, type=KatNodeType.VALUE)
        graph.add_edge(arg_node, group_node, type=KatEdgeType.ARGUMENT, order=order)

    assert unfiller.unfill(group_node, graph) == expected


@pytest.mark.parametrize(
    "arguments,extra,expected",
    (
        pytest.param(
            [NUMBER(1, 2, "1")], [LBRACKET(1, 1), RBRACKET(1, 3)], "[1]", id="[1]",
        ),
        pytest.param(
            [NUMBER(1, 2, "1"), NUMBER(1, 5, "2")],
            [LBRACKET(1, 1), COMMA(1, 3), SPACE(1, 4), RBRACKET(1, 6)],
            "[1, 2]",
            id="[1, 2]",
        ),
    ),
)
def test_array(unfiller, graph, arguments, extra, expected):
    array_node = "myarray"
    graph.add_node(array_node, type=KatNodeType.ARRAY, extra_tokens=extra)
    for order, argument in enumerate(arguments):
        arg_node = f"{array_node}.{order}"
        graph.add_node(arg_node, token=argument, type=KatNodeType.VALUE)
        graph.add_edge(arg_node, array_node, type=KatEdgeType.ARGUMENT, order=order)

    assert unfiller.unfill(array_node, graph) == expected


@pytest.mark.parametrize(
    "directive,element_name,arguments,extra,expected",
    (
        pytest.param(
            NAME(1, 1, "fake_element"),
            NAME(1, 14, "myelement"),
            [],
            [SPACE(1, 13)],
            "fake_element myelement",
            id="fake_element myelement",
        ),
        pytest.param(
            NAME(1, 1, "fake_element"),
            NAME(1, 14, "myelement"),
            [NUMBER(1, 24, "1")],
            [SPACE(1, 13), SPACE(1, 23)],
            "fake_element myelement 1",
            id="fake_element myelement 1",
        ),
        pytest.param(
            NAME(1, 1, "fake_element"),
            NAME(1, 14, "myelement"),
            [NUMBER(1, 24, "1"), NUMBER(1, 26, "2")],
            [SPACE(1, 13), SPACE(1, 23), SPACE(1, 25)],
            "fake_element myelement 1 2",
            id="fake_element myelement 1 2",
        ),
    ),
)
def test_element(unfiller, graph, directive, element_name, arguments, extra, expected):
    element_node = "myelement"
    graph.add_node(
        element_node,
        token=directive,
        name_token=element_name,
        type=KatNodeType.ELEMENT,
        extra_tokens=extra,
    )
    for order, argument in enumerate(arguments):
        arg_node = f"{element_node}.{order}"
        graph.add_node(arg_node, token=argument, type=KatNodeType.VALUE)
        graph.add_edge(arg_node, element_node, type=KatEdgeType.ARGUMENT, order=order)

    assert unfiller.unfill(element_node, graph) == expected


@pytest.mark.parametrize(
    "directive,arguments,extra,expected",
    (
        pytest.param(
            NAME(1, 1, "fake_function"),
            [],
            [LPAREN(1, 14), RPAREN(1, 15)],
            "fake_function()",
            id="fake_function()",
        ),
        pytest.param(
            NAME(1, 1, "fake_function"),
            [NUMBER(1, 15, "1")],
            [LPAREN(1, 14), RPAREN(1, 16)],
            "fake_function(1)",
            id="fake_function(1)",
        ),
        pytest.param(
            NAME(1, 1, "fake_function"),
            [NUMBER(1, 15, "1"), NUMBER(1, 18, "2")],
            [LPAREN(1, 14), COMMA(1, 16), SPACE(1, 17), RPAREN(1, 19)],
            "fake_function(1, 2)",
            id="fake_function(1, 2)",
        ),
    ),
)
def test_function(unfiller, graph, directive, arguments, extra, expected):
    function_node = "myfunction"
    graph.add_node(
        function_node, token=directive, type=KatNodeType.FUNCTION, extra_tokens=extra
    )
    for order, argument in enumerate(arguments):
        arg_node = f"{function_node}.{order}"
        graph.add_node(arg_node, token=argument, type=KatNodeType.VALUE)
        graph.add_edge(arg_node, function_node, type=KatEdgeType.ARGUMENT, order=order)

    assert unfiller.unfill(function_node, graph) == expected
