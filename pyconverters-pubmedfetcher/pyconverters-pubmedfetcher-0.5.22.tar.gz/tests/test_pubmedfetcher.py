from pathlib import Path
from typing import List

from pyconverters_pubmedfetcher.pubmedfetcher import PubmedFetcherConverter, PubmedFetcherParameters
from pymultirole_plugins.v1.schema import Document
from starlette.datastructures import UploadFile

from pyconverters_pubmedfetcher.pubmedfetcher import InputFormat


def test_pubmedfetcher_ids():
    model = PubmedFetcherConverter.get_model()
    model_class = model.construct().__class__
    assert model_class == PubmedFetcherParameters
    converter = PubmedFetcherConverter()
    parameters = PubmedFetcherParameters(input_format=InputFormat.ID_List)
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/list.txt')
    with source.open("r") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'text/plain'), parameters)
        assert len(docs) == 3
        assert docs[0].identifier == '21886606'
        assert docs[1].identifier == '21886599'
        assert docs[1].metadata['doi'] == '10.2174/157015911795017263'
        assert docs[2].identifier == '21886588'
        assert docs[2].metadata['pmc'] == '3137179'


def test_pubmedfetcher_xml():
    converter = PubmedFetcherConverter()
    parameters = PubmedFetcherParameters(input_format=InputFormat.XML_PubmedArticleSet)
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/MedLine2021-09-06-19-04-11.xml')
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'text/xml'), parameters)
        assert len(docs) == 91
        assert docs[0].identifier == '21886606'
