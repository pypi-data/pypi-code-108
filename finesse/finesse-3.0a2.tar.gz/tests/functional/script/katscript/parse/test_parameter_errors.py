"""Test parser parameter error rewriting."""

import pytest
from finesse.script.exceptions import KatScriptError
from .....util import dedent_multiline, escape_full


@pytest.mark.parametrize(
    "script,error",
    (
        # See #335.
        pytest.param(
            dedent_multiline(
                """
                m m1
                pd pd1 1
                """
            ),
            "\nline 2: invalid type for 'pd' argument 'node': expected node, got integer\n"
            "   1: m m1\n"
            "-->2: pd pd1 1\n"
            "             ^\n"
            "Syntax: pd name node pdtype=none",
            id="pd-node-as-number",
        ),
        pytest.param(
            dedent_multiline(
                """
                m m1
                pd pd1 "m1.p1.o"
                """
            ),
            "\nline 2: invalid type for 'pd' argument 'node': expected node, got string\n"
            "   1: m m1\n"
            '-->2: pd pd1 "m1.p1.o"\n'
            "             ^^^^^^^^^\n"
            "Syntax: pd name node pdtype=none",
            id="pd-node-as-string",
        ),
        pytest.param(
            dedent_multiline(
                """
                m m1
                pd pd1 m1
                """
            ),
            "\nline 2: invalid type for 'pd' argument 'node': expected node, got Mirror\n"
            "   1: m m1\n"
            "-->2: pd pd1 m1\n"
            "             ^^\n"
            "Syntax: pd name node pdtype=none",
            id="pd-node-as-port",
        ),
        # See #339.
        pytest.param(
            dedent_multiline(
                """
                m m1
                m m2
                s s1 m1.p1 1 m2.p1
                """
            ),
            "\nline 3: invalid type for 's' argument 'portB': expected port, got integer\n"
            "   2: m m2\n"
            "-->3: s s1 m1.p1 1 m2.p1\n"
            "                 ^\n"
            "Syntax: s name portA=none portB=none L=0.0 nr=1.0 user_gouy_x=none user_gouy_y=none",
            id="space-int-as-port",
        ),
    ),
)
def test_type_error(model, script, error):
    """Incorrect parameter types should display an error that offers allowed types."""
    with pytest.raises(KatScriptError, match=escape_full(error)):
        model.parse(script)


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            dedent_multiline(
                """
                m m1
                pd pd1 m1.p1.o pdtype=none a="b"
                """
            ),
            "\nline 2: 'pd' got an unexpected keyword argument 'a'\n"
            "   1: m m1\n"
            '-->2: pd pd1 m1.p1.o pdtype=none a="b"\n'
            "                                 ^\n"
            "Syntax: pd name node pdtype=none",
            id="unexpected-kwarg",
        ),
        pytest.param(
            dedent_multiline(
                """
                m m1
                pd pd1 m1.p1.o 1 2
                """
            ),
            "\nline 2: 'pd' takes 1 positional argument but 3 were given\n"
            "   1: m m1\n"
            "-->2: pd pd1 m1.p1.o 1 2\n"
            "                     ^ ^\n"
            "Syntax: pd name node pdtype=none",
            id="too-many-args",
        ),
    ),
)
def test_call_value_error(model, script, error):
    """Incorrect call errors."""
    with pytest.raises(KatScriptError, match=escape_full(error)):
        model.parse(script)


@pytest.mark.parametrize(
    "script,error",
    (
        # Single value.
        pytest.param(
            dedent_multiline(
                """
                m m1
                m m2
                s s1 m1.p1 m2.mech
                """
            ),
            "\nline 3: invalid value for 's' argument 'portB': must be an optical port\n"
            "   2: m m2\n"
            "-->3: s s1 m1.p1 m2.mech\n"
            "                 ^^^^^^^\n"
            "Syntax: s name portA=none portB=none L=0.0 nr=1.0 user_gouy_x=none user_gouy_y=none",
            id="mirror-mech-as-optical-port",
        ),
        # Invalid element name. See #342.
        pytest.param(
            dedent_multiline(
                """
                m m1
                m m2
                s m1.p1 m2.p1
                """
            ),
            "\nline 3: invalid value for 's' argument 'name': can only contain alphanumeric and underscore characters\n"
            "   2: m m2\n"
            "-->3: s m1.p1 m2.p1\n"
            "        ^^^^^\n"
            "Syntax: s name portA=none portB=none L=0.0 nr=1.0 user_gouy_x=none user_gouy_y=none",
            id="element-name",
        ),
    ),
)
def test_init_value_error(model, script, error):
    """Errors emitted within an element's __init__."""
    with pytest.raises(KatScriptError, match=escape_full(error)):
        model.parse(script)
