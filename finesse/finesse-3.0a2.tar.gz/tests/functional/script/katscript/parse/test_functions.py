import pytest
from finesse.script import parse
from finesse.script.exceptions import KatScriptError
from .....util import dedent_multiline, escape_full


@pytest.mark.parametrize(
    "script",
    (
        # Positional argument.
        "lambda(1550e-9,)",
        "lambda(1550e-9 ,)",
        "lambda(1550e-9, )",
        "lambda(1550e-9 , )",
        # Keyword argument.
        "modes(maxtem=3,)",
        "modes(maxtem=3 ,)",
        "modes(maxtem=3, )",
        "modes(maxtem=3 , )",
        # Mixed arguments.
        "modes(odd, maxtem=7,)",
        "modes(odd, maxtem=7 ,)",
        "modes(odd, maxtem=7, )",
        "modes(odd, maxtem=7 , )",
    ),
)
def test_trailing_comma(script):
    parse(script)


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            dedent_multiline(
                """
                modes(maxtem=1)
                modes(maxtem=2)
                modes(maxtem=3)
                """
            ),
            (
                "\nlines 1-3: there can only be one 'modes' directive\n"
                "-->1: modes(maxtem=1)\n"
                "      ^^^^^\n"
                "-->2: modes(maxtem=2)\n"
                "      ^^^^^\n"
                "-->3: modes(maxtem=3)\n"
                "      ^^^^^"
            ),
            id="modes",
        ),
    ),
)
def test_duplicate_singular_functions_invalid(script, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        parse(script)


@pytest.mark.parametrize(
    "script",
    (
        pytest.param(
            dedent_multiline(
                """
                l l1
                m m1
                m m2
                link(l1, m1)
                link(m1, m2)
                """
            )
        ),
        pytest.param(
            dedent_multiline(
                """
                l l1
                readout_dc pd1
                butter F 4 lowpass 100
                amplifier G 1
                amplifier K 2
                amplifier L 3

                link(l1, pd1, pd1.DC, F, G, l1.amp)
                link(G.p2, K, F.p1)
                link(G.p2, l1.frq)
                link(K.p2, L, l1.frq)
                """
            )
        ),
    ),
)
def test_duplicate_nonsingular_functions_valid(script):
    """Test that non-singular instructions can be specified multiple times."""
    parse(script)
