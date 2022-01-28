import pytest
from finesse.model import Model
from finesse.parameter import float_parameter
from finesse.symbols import OPERATORS, FUNCTIONS
from finesse.components.general import Connector
from finesse.components.node import NodeDirection, NodeType
from finesse.analysis.actions import Action
from finesse.script.adapter import (
    ItemAdapter,
    ElementDumper,
    ElementFactory,
    ElementSetter,
    ElementDocumenter,
    AnalysisDumper,
    AnalysisFactory,
    AnalysisSetter,
    AnalysisDocumenter,
    CommandMethodSetter,
    CommandMethodDocumenter,
)
from finesse.script.spec import BaseSpec


@pytest.fixture
def spec():
    """Kat spec with no registered elements, commands, etc.

    The spec is shared by builder and generator tests.
    """

    class EmptyTestSpec(BaseSpec):
        """Empty specification class, used by tests."""

    return EmptyTestSpec()


@pytest.fixture
def model():
    class FakeModel(Model):
        """A fake model."""

    return FakeModel()


@pytest.fixture
def fake_adapter():
    return ItemAdapter


@pytest.fixture
def fake_float_parameter():
    return float_parameter


@pytest.fixture
def fake_element_cls():
    """A minimal element.

    Test modules may override this to add more arguments.
    """

    class FakeElement(Connector):
        """A fake element that test modules should override."""

        def __init__(self, name):
            super().__init__(name)

            # Add some ports (required by the parent class).
            self._add_port("p1", NodeType.OPTICAL)
            self.p1._add_node("i", NodeDirection.INPUT)
            self.p1._add_node("o", NodeDirection.OUTPUT)

            self._add_port("p2", NodeType.OPTICAL)
            self.p2._add_node("i", NodeDirection.INPUT)
            self.p2._add_node("o", NodeDirection.OUTPUT)

    return FakeElement


@pytest.fixture
def fake_command_func():
    """A minimal command.

    Test modules may override this to add more arguments.
    """

    def fake_command(model):
        pass

    return fake_command


@pytest.fixture
def fake_analysis_cls():
    """A minimal analysis.

    Test modules may override this to add more arguments.
    """

    # Needs to inherit Action so the generator matches nested analyses correctly.
    class FakeAnalysis(Action):
        def __init__(self):
            pass

        def _requests(self, *args, **kwargs):
            pass

        def _do(self, state):
            pass

    return FakeAnalysis


@pytest.fixture
def fake_element_adapter_factory(fake_adapter):
    def _(
        element_cls,
        full_name="fake_element",
        getter_kwargs={},
        factory_kwargs={},
        setter_kwargs={},
        documenter_kwargs={},
        **adapter_kwargs,
    ):
        return fake_adapter(
            full_name,
            getter=ElementDumper(item_type=element_cls, **getter_kwargs),
            factory=ElementFactory(item_type=element_cls, **factory_kwargs),
            setter=ElementSetter(item_type=element_cls, **setter_kwargs),
            documenter=ElementDocumenter(item_type=element_cls, **documenter_kwargs),
            **adapter_kwargs,
        )

    return _


@pytest.fixture
def fake_analysis_adapter_factory(fake_adapter):
    def _(
        analysis_cls,
        full_name="fake_analysis",
        getter_kwargs={},
        factory_kwargs={},
        setter_kwargs={},
        documenter_kwargs={},
        **adapter_kwargs,
    ):
        return fake_adapter(
            full_name,
            getter=AnalysisDumper(item_type=analysis_cls, **getter_kwargs),
            factory=AnalysisFactory(item_type=analysis_cls, **factory_kwargs),
            setter=AnalysisSetter(item_type=analysis_cls, **setter_kwargs),
            documenter=AnalysisDocumenter(item_type=analysis_cls, **documenter_kwargs),
            **adapter_kwargs,
        )

    return _


@pytest.fixture
def fake_command_adapter_factory(fake_adapter):
    # Assume the passed `command_func` is a function, not method, so we exclude the
    # first argument `model` by default.
    def _(
        command_func,
        full_name="fake_command",
        sig_ignore=("model",),
        setter=None,
        setter_kwargs={},
        documenter=None,
        documenter_kwargs={},
        **adapter_kwargs,
    ):
        if setter is None:
            setter = CommandMethodSetter(
                item_type=command_func, sig_ignore=sig_ignore, **setter_kwargs
            )

        if documenter is None:
            documenter = CommandMethodDocumenter(
                item_type=command_func, sig_ignore=sig_ignore, **documenter_kwargs
            )

        return fake_adapter(
            full_name,
            setter=setter,
            documenter=documenter,
            **adapter_kwargs,
        )

    return _


@pytest.fixture
def fake_noop():
    """A fake operation that should not be called. If called, it triggers an error.

    This is useful for use in tests where the operator is not expected to be called.
    """

    def noop():
        raise RuntimeError(
            "This should not have been called, and indicates a test error. "
            "Make or use a Finesse operation if the results of this function are to be "
            "read."
        )

    return noop


@pytest.fixture
def finesse_binop_add():
    return OPERATORS["__add__"]


@pytest.fixture
def finesse_binop_sub():
    return OPERATORS["__sub__"]


@pytest.fixture
def finesse_binop_mul():
    return OPERATORS["__mul__"]


@pytest.fixture
def finesse_unop_neg():
    return FUNCTIONS["neg"]
