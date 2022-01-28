import pytest
from finesse.symbols import FUNCTIONS
from finesse.script.adapter import (
    ItemDumper,
    SignatureAttributeParameterMixin,
    CommandDump,
)


@pytest.fixture
def fake_command_datastore():
    """Datastore for storing global state in command tests.

    This substitutes the model object in some tests.
    """

    class struct:
        def __init__(self):
            self.a = None
            self.b = None
            self.c = None

    return struct()


@pytest.fixture
def fake_command_datastore_dumper(fake_command_datastore, fake_command_func):
    class FakeCommandDatastoreDumper(SignatureAttributeParameterMixin, ItemDumper):
        def __init__(self):
            super().__init__(item_type=fake_command_func, sig_ignore=("model",))

        def __call__(self, adapter):
            parameters = self.dump_parameters(adapter, fake_command_datastore)

            yield CommandDump(
                adapter=adapter,
                parameters=parameters,
                is_default=all(param.is_default for param in parameters.values()),
            )

    return FakeCommandDatastoreDumper


# Override default command to take two optional arguments.
@pytest.fixture
def fake_command_func(fake_command_datastore):
    def fake_command(model, a, /, b=None, *, c=None):
        fake_command_datastore.a = a
        fake_command_datastore.b = b
        fake_command_datastore.c = c

    return fake_command


# Override default element to take one argument.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a):
            super().__init__(name)
            self.a = a

    return FakeElement


@pytest.fixture
def spec(
    spec,
    fake_command_adapter_factory,
    fake_command_datastore_dumper,
    fake_command_func,
    fake_element_adapter_factory,
    fake_element_cls,
):
    spec.register_command(
        fake_command_adapter_factory(
            fake_command_func,
            short_name="fake_cmd",
            getter=fake_command_datastore_dumper(),
        )
    )
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    # These use Finesse functions directly because they are also used like this in a
    # parametrization below.
    spec.unary_operators["-"] = FUNCTIONS["neg"]
    spec.expression_functions["sin"] = FUNCTIONS["sin"]
    spec.expression_functions["arctan2"] = FUNCTIONS["arctan2"]
    return spec


@pytest.mark.parametrize(
    "args,kwargs,argument_defaults,prefer_keywords,expected",
    (
        # No optional arguments.
        ([None], {}, False, False, "none"),
        ([None], {}, False, True, "none"),
        ([None], {}, True, False, "none, none, c=none"),
        ([None], {}, True, True, "none, b=none, c=none"),
        ([1], {}, False, False, "1"),
        ([1], {}, False, True, "1"),
        ([1], {}, True, False, "1, none, c=none"),
        ([1], {}, True, True, "1, b=none, c=none"),
        # Optional-as-positional arguments.
        ([1, 2], {}, False, False, "1, 2"),
        ([1, 2], {}, False, True, "1, b=2"),
        ([1, 2], {}, True, False, "1, 2, c=none"),
        ([1, 2], {}, True, True, "1, b=2, c=none"),
        ([1, 2], {"c": 3}, False, False, "1, 2, c=3"),
        ([1, 2], {"c": 3}, False, True, "1, b=2, c=3"),
        ([1, 2], {"c": 3}, True, False, "1, 2, c=3"),
        ([1, 2], {"c": 3}, True, True, "1, b=2, c=3"),
        # Optional-as-keyword arguments.
        ([1], {"b": 2}, False, False, "1, 2"),
        ([1], {"b": 2}, False, True, "1, b=2"),
        ([1], {"b": 2}, True, False, "1, 2, c=none"),
        ([1], {"b": 2}, True, True, "1, b=2, c=none"),
        ([1], {"b": 2, "c": 3}, False, False, "1, 2, c=3"),
        ([1], {"b": 2, "c": 3}, False, True, "1, b=2, c=3"),
        ([1], {"b": 2, "c": 3}, True, False, "1, 2, c=3"),
        ([1], {"b": 2, "c": 3}, True, True, "1, b=2, c=3"),
    ),
)
def test_function(
    unbuilder,
    spec,
    args,
    kwargs,
    argument_defaults,
    prefer_keywords,
    expected,
):
    adapter = spec.commands["fake_command"]
    adapter.setter(None, (args, kwargs))
    script = unbuilder.unbuild(
        next(iter(adapter.getter(adapter))),
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == f"fake_command({expected})"


@pytest.mark.parametrize(
    "function,prefer_keywords,expected",
    (
        (FUNCTIONS["neg"](1), False, "fake_element myel -1"),
        (FUNCTIONS["neg"](1), True, "fake_element myel a=-1"),
        (FUNCTIONS["sin"](1), False, "fake_element myel sin(1)"),
        (FUNCTIONS["sin"](1), True, "fake_element myel a=sin(1)"),
        (FUNCTIONS["arctan2"](1, 2), False, "fake_element myel arctan2(1, 2)"),
        (FUNCTIONS["arctan2"](1, 2), True, "fake_element myel a=arctan2(1, 2)"),
    ),
)
def test_expression_function(
    unbuilder,
    model,
    element_dump,
    fake_element_cls,
    function,
    prefer_keywords,
    expected,
):
    model.add(fake_element_cls("myel", function))
    dump = next(iter(element_dump("fake_element", fake_element_cls, model)))
    script = unbuilder.unbuild(dump, prefer_keywords=prefer_keywords)
    assert script == expected
