import pytest
from finesse.script.exceptions import KatParsingError
from ......util import dedent_multiline, escape_full


@pytest.fixture
def spec(spec, fake_analysis_adapter_factory, fake_analysis_cls):
    spec.register_analysis(fake_analysis_adapter_factory(fake_analysis_cls))
    return spec


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            dedent_multiline(
                """
                fake_analysis()
                fake_analysis()
                """
            ),
            "\nlines 1-2: duplicate analysis trees (combine with 'series' or 'parallel')\n"
            "-->1: fake_analysis()\n"
            "      ^^^^^^^^^^^^^\n"
            "-->2: fake_analysis()\n"
            "      ^^^^^^^^^^^^^",
            id="xaxis",
        ),
    ),
)
def test_multiple_analyses_invalid(compiler, script, error):
    with pytest.raises(KatParsingError, match=escape_full(error)):
        compiler.compile(script)
