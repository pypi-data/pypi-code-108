import pytest
from finesse.script.compiler import KatCompiler
from finesse.script.generator import KatUnbuilder


@pytest.fixture
def compiler(spec):
    return KatCompiler(spec=spec)


@pytest.fixture
def regenerate(spec):
    """Regenerate a model."""
    unbuilder = KatUnbuilder(spec=spec)

    def _(model):
        return unbuilder.unbuild(model, ref_graph=model.syntax_graph)

    return _


@pytest.fixture
def regenerate_item(spec):
    """Regenerate an item within a model."""
    unbuilder = KatUnbuilder(spec=spec)

    def _(item, model, ref_node):
        return unbuilder.unbuild(item, ref_graph=model.syntax_graph, ref_node=ref_node)

    return _
