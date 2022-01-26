import json
from pathlib import Path

from pymultirole_plugins.v1.schema import Document
from starlette.responses import Response

from pyformatters_bel_table.bel_table import BELTableFormatter, BELTableParameters, OutputFormat


def test_xlsx():
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/bel_entities_rel0.json')
    with source.open("r") as fin:
        docs = json.load(fin)
        doc = Document(**docs[0])
        formatter = BELTableFormatter()
        options = BELTableParameters(format=OutputFormat.xlsx)
        resp: Response = formatter.format(doc, options)
        assert resp.status_code == 200
        assert resp.media_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        result = Path(testdir, 'data/bel_entities_rel0.xlsx')
        with result.open("wb") as fout:
            fout.write(resp.body)
