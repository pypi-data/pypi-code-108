import pytest
from finesse.script.exceptions import KatScriptError
from ......util import escape_full


# Override default element to take two arguments.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a=None, b=None):
            super().__init__(name)
            self.a = a
            self.b = b

    return FakeElement


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    return spec


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            "fake_element myelement a=1 a=2",
            (
                "\nline 1: duplicate arguments with key 'a'\n"
                "-->1: fake_element myelement a=1 a=2\n"
                "                             ^   ^\n"
                "Syntax: fake_element name a=none b=none"
            ),
            id="duplicate keyword argument",
        ),
        pytest.param(
            "fake_element myelement a=1 b=2 a=3",
            (
                "\nline 1: duplicate arguments with key 'a'\n"
                "-->1: fake_element myelement a=1 b=2 a=3\n"
                "                             ^       ^\n"
                "Syntax: fake_element name a=none b=none"
            ),
            id="duplicate keyword argument, out of order",
        ),
        pytest.param(
            "fake_element myelement a=1 b=2 a=3 b=4",
            (
                "\nline 1: duplicate arguments with keys 'a' and 'b'\n"
                "-->1: fake_element myelement a=1 b=2 a=3 b=4\n"
                "                             ^   ^   ^   ^\n"
                "Syntax: fake_element name a=none b=none"
            ),
            id="multiple duplicate keyword arguments",
        ),
    ),
)
def test_duplicate_argument_error(compiler, script, error):
    """Test duplicate arguments get caught in the resolving stage.

    Duplicate arguments are checked in the resolver because later they get added into
    dicts for passing to the setter where duplicate keys would otherwise get silently
    overwritten.
    """
    with pytest.raises(KatScriptError, match=escape_full(error)):
        compiler.compile(script)
