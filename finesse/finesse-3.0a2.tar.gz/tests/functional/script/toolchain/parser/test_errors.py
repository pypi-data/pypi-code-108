import pytest
from finesse.script.exceptions import KatSyntaxError
from .....util import dedent_multiline, escape_full


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            "myelement @",
            (
                "\nline 1: illegal character '@'\n"
                "-->1: myelement @\n"
                "                ^"
            ),
            id="illegal-character",
        ),
        pytest.param(
            dedent_multiline(
                """
                laser l1 P=1
                xaxis(l1.f, lin, 10*, 40k, 20)
                """
            ),
            # See #265.
            (
                "\nline 2: syntax error\n"
                "   1: laser l1 P=1\n"
                "-->2: xaxis(l1.f, lin, 10*, 40k, 20)\n"
                "                          ^"
            ),
            id="incomplete-expression",
        ),
        pytest.param(
            "modes ()",
            ("\nline 1: space not allowed here\n" "-->1: modes ()\n" "           ^"),
            id="space-after-function-0-params",
        ),
        pytest.param(
            "modes (maxtem=1)",
            (
                "\nline 1: space not allowed here\n"
                "-->1: modes (maxtem=1)\n"
                "           ^"
            ),
            id="space-after-function-1-param",
        ),
        pytest.param(
            "modes (odd, maxtem=1)",
            (
                "\nline 1: space not allowed here\n"
                "-->1: modes (odd, maxtem=1)\n"
                "           ^"
            ),
            id="space-after-function-2-params",
        ),
        # Too many trailing commas.
        pytest.param(
            "modes(odd, maxtem=1,,)",
            (
                "\nline 1: syntax error\n"
                "-->1: modes(odd, maxtem=1,,)\n"
                "                          ^"
            ),
            id="two-trailing-commas-nospace",
        ),
        pytest.param(
            "modes(odd, maxtem=1 ,,)",
            (
                "\nline 1: syntax error\n"
                "-->1: modes(odd, maxtem=1 ,,)\n"
                "                           ^"
            ),
            id="two-trailing-commas-prespace",
        ),
        pytest.param(
            "modes(odd, maxtem=1, ,)",
            (
                "\nline 1: syntax error\n"
                "-->1: modes(odd, maxtem=1, ,)\n"
                "                           ^"
            ),
            id="two-trailing-commas-innerspace",
        ),
        pytest.param(
            "modes(odd, maxtem=1,, )",
            (
                "\nline 1: syntax error\n"
                "-->1: modes(odd, maxtem=1,, )\n"
                "                          ^"
            ),
            id="two-trailing-commas-postspace",
        ),
        pytest.param(
            "modes(odd, maxtem=1 , , )",
            (
                "\nline 1: syntax error\n"
                "-->1: modes(odd, maxtem=1 , , )\n"
                "                            ^"
            ),
            id="two-trailing-commas-preinnerpostspace",
        ),
        pytest.param(
            "modes(odd, maxtem=1,,,,)",
            (
                "\nline 1: syntax error\n"
                "-->1: modes(odd, maxtem=1,,,,)\n"
                "                          ^"
            ),
            id="four-trailing-commas",
        ),
        pytest.param(
            dedent_multiline(
                """
                modes(
                    odd,
                    maxtem=1,
                    # comment
                    ,
                )
                """
            ),
            (
                "\nline 5: syntax error\n"
                "   4:     # comment\n"
                "-->5:     ,\n"
                "          ^"
            ),
            id="two-trailing-commas-comment-multiline",
        ),
        # Numbers.
        pytest.param(
            "m m1 01",
            (
                "\nline 1: leading zeros in integers are not permitted\n"
                "-->1: m m1 01\n"
                "           ^"
            ),
            id="integer-leading-zeros-1",
        ),
        pytest.param(
            "m m1 001",
            (
                "\nline 1: leading zeros in integers are not permitted\n"
                "-->1: m m1 001\n"
                "           ^^"
            ),
            id="integer-leading-zeros-2",
        ),
        pytest.param(
            "m m1 0.0.0",
            (
                "\nline 1: invalid number syntax\n"
                "-->1: m m1 0.0.0\n"
                "              ^^"
            ),
            id="invalid-float",
        ),
    ),
)
def test_syntax_error(parser, script, error):
    with pytest.raises(KatSyntaxError, match=escape_full(error)):
        parser.parse(script)
