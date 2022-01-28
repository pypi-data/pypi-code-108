import pytest
from finesse.script.exceptions import KatScriptError
from ......util import dedent_multiline, escape_full


# Override default element to take one argument.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a):
            super().__init__(name)
            self.a = a

    return FakeElement


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls, fake_noop):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    spec.binary_operators["-"] = fake_noop
    spec.unary_operators["-"] = fake_noop
    return spec


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            dedent_multiline(
                """
                fake_element myelement1 &myelement2.a
                fake_element myelement2 &myelement1.a
                """
            ),
            (
                "\nlines 1-2: cyclic parameters\n"
                "-->1: fake_element myelement1 &myelement2.a\n"
                "                              ^^^^^^^^^^^^^\n"
                "-->2: fake_element myelement2 &myelement1.a\n"
                "                              ^^^^^^^^^^^^^"
            ),
            id="cycle between two elements",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_element myelement1 &myelement2.a
                fake_element myelement2 1-&myelement1.a
                """
            ),
            (
                "\nlines 1-2: cyclic parameters\n"
                "-->1: fake_element myelement1 &myelement2.a\n"
                "                              ^^^^^^^^^^^^^\n"
                "-->2: fake_element myelement2 1-&myelement1.a\n"
                "                                ^^^^^^^^^^^^^"
            ),
            id="cycle between two elements (one inside expression)",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_element myelement1 &myelement2.a
                fake_element myelement2 -&myelement1.a
                """
            ),
            (
                "\nlines 1-2: cyclic parameters\n"
                "-->1: fake_element myelement1 &myelement2.a\n"
                "                              ^^^^^^^^^^^^^\n"
                "-->2: fake_element myelement2 -&myelement1.a\n"
                "                               ^^^^^^^^^^^^^"
            ),
            id="cycle between two elements (one inside unary function)",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_element myelement1 &myelement2.a
                fake_element myelement2 &myelement3.a
                fake_element myelement3 &myelement4.a
                fake_element myelement4 &myelement1.a
                """
            ),
            (
                "\nlines 1-4: cyclic parameters\n"
                "-->1: fake_element myelement1 &myelement2.a\n"
                "                              ^^^^^^^^^^^^^\n"
                "-->2: fake_element myelement2 &myelement3.a\n"
                "                              ^^^^^^^^^^^^^\n"
                "-->3: fake_element myelement3 &myelement4.a\n"
                "                              ^^^^^^^^^^^^^\n"
                "-->4: fake_element myelement4 &myelement1.a\n"
                "                              ^^^^^^^^^^^^^"
            ),
            id="cycle between four elements",
        ),
    ),
)
def test_cycles_invalid(compiler, script, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        compiler.compile(script)
