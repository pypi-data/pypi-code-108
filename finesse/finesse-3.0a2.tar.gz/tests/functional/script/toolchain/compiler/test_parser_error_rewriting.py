"""Test `reraise_in_spec_context` which rewrites parsing errors with more spec-specific
information."""

import pytest
from finesse.script.exceptions import KatScriptError
from .....util import escape_full


# Override default element to take two arguments.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a, b=None):
            super().__init__(name)
            self.a = a
            self.b = b

    return FakeElement


# Override default command to take two arguments (in addition to `model`).
@pytest.fixture
def fake_command_func():
    def fake_command(model, a, b=None):
        pass

    return fake_command


# Override default command to take two arguments.
@pytest.fixture
def fake_analysis_cls(fake_analysis_cls):
    class FakeAnalysis(fake_analysis_cls):
        def __init__(self, a, b=None):
            super().__init__()

    return FakeAnalysis


@pytest.fixture
def spec(
    spec,
    fake_element_adapter_factory,
    fake_element_cls,
    fake_command_adapter_factory,
    fake_command_func,
    fake_analysis_adapter_factory,
    fake_analysis_cls,
):
    # Specify some short names to test errors re-use these.
    spec.register_element(
        fake_element_adapter_factory(
            fake_element_cls, full_name="fake_element", short_name="fake_el"
        )
    )
    spec.register_command(
        fake_command_adapter_factory(
            fake_command_func, full_name="fake_command", short_name="fake_cmd"
        )
    )
    spec.register_analysis(
        fake_analysis_adapter_factory(
            fake_analysis_cls, full_name="fake_analysis", short_name="fake_an"
        )
    )
    return spec


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            "fake_element a=1",
            "\nline 1: 'fake_element' should be written in the form 'fake_element name a b=none'\n"
            "-->1: fake_element a=1\n"
            "      ^^^^^^^^^^^^",
            id="element-without-name",
        ),
        pytest.param(
            "fake_el a=1",
            "\nline 1: 'fake_el' should be written in the form 'fake_el name a b=none'\n"
            "-->1: fake_el a=1\n"
            "      ^^^^^^^",
            id="element-without-name-short",
        ),
        pytest.param(
            "fake_command 1",
            "\nline 1: 'fake_command' should be written in the form 'fake_command(a, b=none)'\n"
            "-->1: fake_command 1\n"
            "      ^^^^^^^^^^^^",
            id="command-without-opening-parenthesis-arg",
        ),
        pytest.param(
            "fake_command even 4",
            "\nline 1: 'fake_command' should be written in the form 'fake_command(a, b=none)'\n"
            "-->1: fake_command even 4\n"
            "      ^^^^^^^^^^^^",
            id="command-without-opening-parenthesis-args",
        ),
        pytest.param(
            "fake_command a=1",
            "\nline 1: 'fake_command' should be written in the form 'fake_command(a, b=none)'\n"
            "-->1: fake_command a=1\n"
            "      ^^^^^^^^^^^^",
            id="command-without-opening-parenthesis-kwarg",
        ),
        pytest.param(
            "fake_cmd 1",
            "\nline 1: 'fake_cmd' should be written in the form 'fake_cmd(a, b=none)'\n"
            "-->1: fake_cmd 1\n"
            "      ^^^^^^^^",
            id="command-without-opening-parenthesis-short",
        ),
        pytest.param(
            "fake_analysis a=1",
            "\nline 1: 'fake_analysis' should be written in the form 'fake_analysis(a, b=none)'\n"
            "-->1: fake_analysis a=1\n"
            "      ^^^^^^^^^^^^^",
            id="analysis-without-opening-parenthesis",
        ),
        pytest.param(
            "fake_an a=1",
            "\nline 1: 'fake_an' should be written in the form 'fake_an(a, b=none)'\n"
            "-->1: fake_an a=1\n"
            "      ^^^^^^^",
            id="analysis-without-opening-parenthesis-short",
        ),
        # Even though a name or '(' is missing, the earlier error is thrown.
        pytest.param(
            "__unregistered_directive__ a=1",
            "\nline 1: unknown element or function '__unregistered_directive__'\n"
            "-->1: __unregistered_directive__ a=1\n"
            "      ^^^^^^^^^^^^^^^^^^^^^^^^^^",
            id="unregistered-directive",
        ),
    ),
)
def test_directive_missing_name_or_parenthesis_syntax_error(compiler, script, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        compiler.compile(script)
