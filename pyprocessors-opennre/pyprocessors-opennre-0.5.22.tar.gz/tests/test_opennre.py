import copy
import gzip
import json
import os
from collections import namedtuple
from itertools import chain, islice, combinations
from pathlib import Path
from typing import List
os.environ["MODELS_DIR"] = os.path.join(os.path.dirname(__file__), '../models')

import pandas as pd
import pytest as pytest
from pybel.dsl import Pathology, BiologicalProcess, Protein, Abundance, ProteinModification
from pymultirole_plugins.v1.schema import Document, DocumentList
from pyprocessors_opennre.opennre_proc import OpenNREProcessor, \
    OpenNREParameters, OpenNREModel, get_model
from tqdm import tqdm


# @pytest.mark.skip(reason="Not a test")
def test_opennre():
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/bel_entities.json')
    parameters = OpenNREParameters(model=OpenNREModel.scai_biobert_base_cased_entity)
    annotator = OpenNREProcessor()
    with source.open("r") as fin:
        data = json.load(fin)
        ifile = 0
        for jdocs in tqdm(chunks(data, 100)):
            docs: List[Document] = annotator.process([Document(**jdoc) for jdoc in jdocs], parameters)
            result = Path(testdir, f"data/bel_entities_rel{ifile}.json")
            ifile += 1
            dl = DocumentList(__root__=docs)
            with result.open("w") as fout:
                print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


def chunks(iterable, size=10):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


@pytest.mark.skip(reason="Not a test")
def test_scai_ef():
    Name2Class = {
        'Abundance': Abundance,
        'Protein': Protein,
        'BiologicalProcess': BiologicalProcess,
        'Pathology': Pathology
    }
    OpenNREEntity = namedtuple('OpenNREEntity', ['name', 'type', 'pos'])
    m = get_model(OpenNREModel.scai_biobert_base_cased_entity)
    testdir = Path('/media/olivier/DATA/corpora/SCAI/MedlineCorpus-Schizophrenia-BipolarDisorder-20210907')
    for pubmed_gz in tqdm(testdir.glob('*_opennre.json.gz')):
        with gzip.open(pubmed_gz) as fin:
            docs = json.load(fin)
            series = []
            for doc in docs:
                slist = {}
                pmods = {}
                stext = doc['EvidenceSentence']
                for e in doc['Entities']:
                    name = e['name'] or stext[e['start']:e['end']]
                    if e['class']:
                        a = OpenNREEntity(e['name'], e['class'], (e['start'], e['end']))
                        if e['class'] == "ModType":
                            if e['name']:
                                c = ProteinModification(e['name'])
                                pmods[a] = c
                        elif e['class'] not in ['Location', 'Specie']:
                            clazz = Name2Class[e['class']]
                            identifier = None
                            if 'identifier' in e:
                                identifier = (e['identifier'].split(':'))[-1]
                            c = clazz(namespace=e.get('namespace', 'UNKNOWN'), name=name,
                                      identifier=identifier)
                            slist[a] = c
                if len(slist) > 1:
                    if pmods:
                        prots = {a: c for a, c in slist.items() if isinstance(c, Protein)}
                        for prot, cprot in prots.items():
                            for pmod, cpmod in pmods.items():
                                result = m.infer({
                                    'text': stext,
                                    'h': pmod._asdict(),
                                    't': prot._asdict()
                                })
                                if result[0] == 'modifies' and result[1] > 0.8:
                                    slist[prot] = Protein(namespace=cprot.namespace, name=cprot.name,
                                                          identifier=cprot.identifier, variants=[cpmod])
                    for pair1, pair2 in combinations(slist.items(), 2):
                        a1, class1 = pair1
                        a2, class2 = pair2
                        if a1.type == a2.type and class1.namespace == class2.namespace and (
                                class1.identifier == class2.identifier or class1.name == class2.name):
                            break
                        results = []
                        results.append(m.infer({
                            'text': stext,
                            'h': a1._asdict(),
                            't': a2._asdict()
                        }))
                        results.append(m.infer({
                            'text': stext,
                            'h': a2._asdict(),
                            't': a1._asdict()
                        }))
                        max_idx = 0 if results[0][1] > results[1][1] else 1
                        relation, score = results[max_idx]
                        if relation != 'NoRelation' and score > 0.8:
                            source = class1 if max_idx == 0 else class2
                            source_pos = a1.pos if max_idx == 0 else a2.pos
                            target = class2 if max_idx == 0 else class1
                            target_pos = a2.pos if max_idx == 0 else a1.pos
                            line = copy.deepcopy(doc)
                            del line["Entities"]
                            line['Subject'] = str(source)
                            line['Subject.start'] = str(source_pos[0])
                            line['Subject.end'] = str(source_pos[1])
                            line['Subject.text'] = stext[source_pos[0]:source_pos[1]]
                            line['Relation'] = relation
                            line['Object'] = str(target)
                            line['Object.start'] = str(target_pos[0])
                            line['Object.end'] = str(target_pos[1])
                            line['Object.text'] = stext[target_pos[0]:target_pos[1]]
                            line['Score'] = str(score)
                            series.append(line)
            df = pd.DataFrame.from_records(series)
            excel_file = pubmed_gz.with_suffix(".xlsx")
            df.to_excel(str(excel_file),
                        columns=['Subject', 'Subject.start', 'Subject.end', 'Subject.text', 'Relation',
                                 'Object', 'Object.start', 'Object.end', 'Object.text', 'Score', 'PubMedID', 'EvidenceSentence',
                                 'PublicationTitle',
                                 'Journal'])
