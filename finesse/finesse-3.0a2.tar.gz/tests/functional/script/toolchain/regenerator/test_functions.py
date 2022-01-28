import pytest
from finesse.symbols import FUNCTIONS
from finesse.script.adapter import (
    ItemDumper,
    SignatureAttributeParameterMixin,
    CommandDump,
)
from .....util import dedent_multiline


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


@pytest.fixture
def spec(
    spec,
    fake_command_adapter_factory,
    fake_command_datastore_dumper,
    fake_command_func,
):
    spec.register_command(
        fake_command_adapter_factory(
            fake_command_func,
            short_name="fake_cmd",
            getter=fake_command_datastore_dumper(),
        )
    )
    # These use Finesse functions directly because they are also used like this in a
    # parametrization below.
    spec.unary_operators["-"] = FUNCTIONS["neg"]
    spec.expression_functions["sin"] = FUNCTIONS["sin"]
    spec.expression_functions["arctan2"] = FUNCTIONS["arctan2"]
    return spec


@pytest.mark.parametrize(
    "script",
    (
        # Aliases and whitespace.
        ("fake_command(1)"),
        ("fake_command(  1   )"),
        ("fake_cmd(1)"),
        ("fake_cmd(  1)"),
        # Optional-as-positional arguments.
        ("fake_command(1, 2)"),
        ("fake_command(1.,  2.)"),
        ("fake_command(  1.,  2. , c=3)"),
        # Optional-as-keyword arguments.
        ("fake_command(1, b=2)"),
        ("fake_command(1.1, b=2)"),
        ("fake_command(1.,  b=2.)"),
        ("fake_command(1.,      b=2.)"),
        # Multi-line.
        (
            dedent_multiline(
                """
                fake_command(
                    1.,
                    b=2.
                )
                """
            )
        ),
        (
            dedent_multiline(
                """
                fake_command(
                    1.,  # comment
                      # another comment
                        b=2.
                )
                """
            )
        ),
    ),
)
def test_function(
    compiler, regenerate_item, spec, fake_command_datastore_dumper, script
):
    model = compiler.compile(script)
    dumper = fake_command_datastore_dumper()
    dump = next(iter(dumper(spec.commands["fake_command"])))
    assert regenerate_item(dump, model, "kat.0") == script
