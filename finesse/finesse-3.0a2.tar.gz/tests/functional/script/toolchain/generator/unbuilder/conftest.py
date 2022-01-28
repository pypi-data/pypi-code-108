import pytest
from finesse.script.compiler import KatCompiler
from finesse.script.spec import ElementDumper, AnalysisDumper


@pytest.fixture
def compiler(spec):
    return KatCompiler(spec=spec)


@pytest.fixture
def element_dump(spec):
    def _(directive, element_cls, model):
        element_dumper = ElementDumper(item_type=element_cls)
        return element_dumper(spec.elements[directive], model)

    return _


@pytest.fixture
def analysis_dump(spec):
    def _(directive, analysis_cls, model):
        analysis_dumper = AnalysisDumper(item_type=analysis_cls)
        return analysis_dumper(spec.analyses[directive], model)

    return _
