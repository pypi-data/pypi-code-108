import json
import os
from collections import namedtuple
from enum import Enum
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Type, List, cast

import torch
from collections_extended import RangeMap
from pybel.dsl import Abundance, Protein, BiologicalProcess, Pathology, ProteinModification
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.processor import ProcessorParameters, ProcessorBase
from pymultirole_plugins.v1.schema import Document, Annotation
from pyprocessors_opennre.opennre.encoder import BERTEntityEncoder
from pyprocessors_opennre.opennre.model import SoftmaxNN
from pyprocessors_opennre.opennre.pretrain import download_bert_base_uncased

_home = os.path.expanduser('~')
xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or os.path.join(_home, '.cache')
MODELS_DIR = os.environ.get('MODELS_DIR', 'models')

class OpenNREModel(str, Enum):
    #    scai_bert_uncased_entity = 'scai_bert-base-uncased_entity'
    scai_biobert_base_cased_entity = 'scai_biobert-base-cased_entity'


class OpenNREParameters(ProcessorParameters):
    model: OpenNREModel = Field(OpenNREModel.scai_biobert_base_cased_entity,
                                description="""Which [OpenNRE](
                            https://github.com/thunlp/OpenNRE)  model to use.""")


OpenNREEntity = namedtuple('OpenNREEntity', ['name', 'type', 'pos'])
Name2Class = {
    'Abundance': Abundance,
    'Protein': Protein,
    'BiologicalProcess': BiologicalProcess,
    'Pathology': Pathology
}


class OpenNREProcessor(ProcessorBase):
    """[OpenNRE](https://github.com/thunlp/OpenNRE) Relation extractor.
    """

    # cache_dir = os.path.join(xdg_cache_home, 'trankit')

    def process(self, documents: List[Document], parameters: ProcessorParameters) \
            -> List[Document]:
        params: OpenNREParameters = \
            cast(OpenNREParameters, parameters)

        m: SoftmaxNN = get_model(params.model)

        for document in documents:
            if document.sentences and document.annotations:
                relations = []
                sent_map = RangeMap()
                for isent, sent in enumerate(document.sentences):
                    sent_map[sent.start:sent.end] = []
                for a in document.annotations:
                    alist = sent_map[a.start]
                    alist.append(a)
                for isent, (sstart, sstop, slist) in enumerate(sent_map.ranges()):
                    sent = document.sentences[isent]
                    smap = {}
                    pmods = {}
                    stext = document.text[sent.start:sent.end]
                    for e in slist:
                        name = e.properties.get('name', None) or document.text[e.start:e.end]
                        if e.label:
                            a = OpenNREEntity(name, e.label, (e.start - sstart, e.end - sstart))
                            if e.label == "ModType":
                                if name:
                                    c = ProteinModification(name)
                                    pmods[a] = c
                            elif e.label in Name2Class.keys():
                                clazz = Name2Class[e.label]
                                identifier = None
                                if 'identifier' in e.properties:
                                    identifier = (e.properties['identifier'].split(':'))[-1]
                                c = clazz(namespace=e.properties.get('namespace', 'UNKNOWN'), name=name,
                                          identifier=identifier)
                                smap[a] = c
                    if len(smap) > 1:
                        if pmods:
                            prots = {a: c for a, c in smap.items() if isinstance(c, Protein)}
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
                        for pair1, pair2 in combinations(smap.items(), 2):
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
                                rel = Annotation(label='Relation', labelName='relation', start=sent.start, end=sent.end, properties={})
                                rel.properties['Subject'] = str(source)
                                rel.properties['Subject.start'] = str(source_pos[0])
                                rel.properties['Subject.end'] = str(source_pos[1])
                                rel.properties['Subject.text'] = stext[source_pos[0]:source_pos[1]]
                                rel.properties['Relation'] = relation
                                rel.properties['Object'] = str(target)
                                rel.properties['Object.start'] = str(target_pos[0])
                                rel.properties['Object.end'] = str(target_pos[1])
                                rel.properties['Object.text'] = stext[target_pos[0]:target_pos[1]]
                                rel.properties['Score'] = str(score)
                                relations.append(rel)
                document.annotations.extend(relations)
        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return OpenNREParameters


@lru_cache(maxsize=None)
def get_model(model):
    modeldir = Path(MODELS_DIR)
    root_path = str(modeldir)
    download_bert_base_uncased(root_path=root_path)
    rel2id_path = os.path.join(root_path, f"{model.value}.rel2id")
    with open(rel2id_path) as fin:
        rel2id = json.load(fin)
    # sentence_encoder = BERTEntityEncoder(
    #     max_length=80, pretrain_path='bert-base-uncased')
    sentence_encoder = BERTEntityEncoder(
        max_length=80, pretrain_path="dmis-lab/biobert-base-cased-v1.1")
    ckpt = os.path.join(root_path, f"{model.value}.pth.tar")
    m = SoftmaxNN(sentence_encoder, len(rel2id), rel2id)
    m.load_state_dict(torch.load(ckpt, map_location='cpu')['state_dict'])
    return m
