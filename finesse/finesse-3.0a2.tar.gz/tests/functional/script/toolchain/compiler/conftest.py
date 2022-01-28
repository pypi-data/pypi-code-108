import pytest
from finesse.script.compiler import KatCompiler
from ....diff import assert_graph_matches_def


@pytest.fixture
def compiler(spec):
    return KatCompiler(spec=spec)


@pytest.fixture
def assert_graphs_match(compiler):
    def matcher(script, reference_graph):
        compiler.compile(script)
        assert_graph_matches_def(compiler.graph, reference_graph)

    return matcher
