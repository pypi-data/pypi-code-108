from pathlib import Path

from progress.bar import Bar
from pyimporters_plugins.base import Term

from pyimporters_json.json import JSONKnowledgeParser, JSONOptionsModel


def test_json():
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/organization_en.json')
    parser = JSONKnowledgeParser()
    options = JSONOptionsModel()
    concepts = list(parser.parse(source, options.dict(), Bar('Processing')))
    assert len(concepts) == 1527
    c7: Term = concepts[7]
    assert c7.identifier == 'afporganization:2021'
    assert c7.preferredForm == 'REYNOLDS AMERICAN'
    assert len(c7.properties['altForms']) == 1
    assert 'Reynolds American' in c7.properties['altForms']
