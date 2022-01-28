import copy
import json
from collections import defaultdict
from pathlib import Path
from typing import List

import pytest
from pyconverters_newsml.newsml import NewsMLConverter, NewsMLParameters
from pymultirole_plugins.v1.schema import Document, DocumentList
from starlette.datastructures import UploadFile


def test_newsml_text():
    model = NewsMLConverter.get_model()
    model_class = model.construct().__class__
    assert model_class == NewsMLParameters
    converter = NewsMLConverter()
    parameters = NewsMLParameters(subjects_as_metadata="afpperson,afporganization,afplocation")
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/text_only.xml')
    with source.open("r") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'text/xml'), parameters)
        assert len(docs) == 1
        doc0 = docs[0]
        assert doc0.metadata['nature'] == 'text'
        assert doc0.metadata['lang'] == 'es'
        assert 'Agence américaine d\'information' in doc0.metadata['afporganization']
        assert 'New York' in doc0.metadata['afplocation']
        assert doc0.categories is None


def test_newsml_pics():
    model = NewsMLConverter.get_model()
    model_class = model.construct().__class__
    assert model_class == NewsMLParameters
    converter = NewsMLConverter()
    parameters = NewsMLParameters(subjects_as_metadata="medtop,afpperson,afporganization,afplocation",
                                  mediatopics_as_categories=True)
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/text_and_pics.xml')
    with source.open("r") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'text/xml'), parameters)
        assert len(docs) == 7
        doc0 = docs[0]
        assert doc0.metadata['nature'] == 'text'
        assert doc0.metadata['lang'] == 'fr'
        assert 'national elections' in doc0.metadata['medtop']
        assert 'civil unrest' in doc0.metadata['medtop']
        cat_labels = [cat.label for cat in doc0.categories]
        assert ['national elections' in cat_label for cat_label in cat_labels]
        assert ['civil unrest' in cat_label for cat_label in cat_labels]
        doc1 = docs[1]
        assert doc1.metadata['nature'] == 'video'
        assert doc1.metadata['lang'] == 'fr'
        assert 'national elections' in doc1.metadata['medtop']
        assert 'heads of state' in doc1.metadata['medtop']
        cat_labels = [cat.label for cat in doc1.categories]
        assert ['national elections' in cat_label for cat_label in cat_labels]
        assert ['heads of state' in cat_label for cat_label in cat_labels]


@pytest.mark.skip(reason="Not a test")
def test_parse_xml():
    converter = NewsMLConverter()
    parameters = NewsMLParameters(subjects_as_metadata="medtop,afpperson,afporganization,afplocation",
                                  mediatopics_as_categories=True)
    input_path = Path("/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_FR")
    # input_path = Path("/media/olivier/DATA/corpora/AFP/extract_9ba8e44c-0cfc-45fe-a3ed-9bfa41a52fc4_2")
    output_path = Path("/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_FR_PARSED")
    # output_path = Path("/media/olivier/DATA/corpora/AFP/extract_9ba8e44c-0cfc-45fe-a3ed-9bfa41a52fc4_2-parsed")
    for year in input_path.glob("*"):
        if year.is_dir():
            for month in year.iterdir():
                data = defaultdict(list)
                for f in month.rglob("*.xml"):
                    with f.open("r") as fin:
                        docs: List[Document] = converter.convert(UploadFile(f.name, fin, 'text/xml'), parameters)
                        for doc in docs:
                            data[doc.metadata['lang']].append(doc)
                for lang, ldocs in data.items():
                    output_dir = Path(output_path) / lang / year.name
                    output_dir.mkdir(parents=True, exist_ok=True)
                    dl = DocumentList(__root__=ldocs)
                    output_file = output_dir / Path(month.name).with_suffix(".json")
                    with output_file.open("w") as fout:
                        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


@pytest.mark.skip(reason="Not a test")
def test_parse_categories():
    input_path = Path("/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_FR_PARSED")
    # input_path = Path("/media/olivier/DATA/corpora/AFP/extract_9ba8e44c-0cfc-45fe-a3ed-9bfa41a52fc4_2-parsed")
    output_path = Path("/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_FR_CAT")
    # output_path = Path("/media/olivier/DATA/corpora/AFP/extract_9ba8e44c-0cfc-45fe-a3ed-9bfa41a52fc4_2-categ")
    for lang in input_path.glob("*"):
        if lang.is_dir():
            for year in lang.iterdir():
                for f in year.rglob("*.json"):
                    with f.open("r") as fin:
                        jdocs = json.load(fin)
                        docs: List[Document] = [Document(**jdoc) for jdoc in jdocs]
                        lvl_docs = defaultdict(list)
                        for doc in docs:
                            lvl_categories = defaultdict(list)
                            if doc.categories:
                                lnames = [c.labelName.split('_') for c in doc.categories]
                                level1 = [codes[0] for codes in lnames if len(codes) == 1]
                                lvl_categories['_'] = [c for c in doc.categories if c.labelName in level1]
                                for lvl1 in level1:
                                    lvl_categories[lvl1] = [c for c in doc.categories if
                                                            c.labelName.startswith(f"{lvl1}_")]
                                for lvl, cats in lvl_categories.items():
                                    newdoc = copy.deepcopy(doc)
                                    newdoc.categories = cats
                                    lvl_docs[lvl].append(newdoc)
                        for lvl, ldocs in lvl_docs.items():
                            if len(ldocs) > 0:
                                output_dir = Path(output_path) / lang.name / year.name / lvl
                                output_dir.mkdir(parents=True, exist_ok=True)
                                dl = DocumentList(__root__=ldocs)
                                output_file = output_dir / Path(f.name).with_suffix(".json")
                                with output_file.open("w") as fout:
                                    print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
