import yaml
import numpy as np
import pandas as pd
from pathlib import Path

from pydantic import BaseModel, validator
from typing import List, Dict, Union
from label_studio_sdk.labelops.graph import LabelGraphDB
from snorkel.labeling import LFAnalysis
from snorkel.labeling.model import MajorityLabelVoter


# lg = LabelGraphDB('bolt://localhost:7687', 'neo4j', 'password')

lg = LabelGraphDB('bolt://52.22.253.215:7687', 'neo4j', 'survive-report-domino-juice-first-1555')


class Pattern(BaseModel):
    query: Dict

    @validator('query')
    def validate_query(cls, v):
        return v

    def retrieve(self):
        pass


class Regex(Pattern):

    @validator('query')
    def validate_query(cls, v):
        return v

    def retrieve(self):
        return lg.match_data_regex(self.query)


class Entities(Pattern):
    query: List[Dict]

    @validator('query')
    def validate_query(cls, v):
        return v

    def retrieve(self):
        return lg.match_labels(self.query)


class LabelOp(BaseModel):
    name: str
    label: str
    pattern: Pattern

    class Config:
        arbitrary_types_allowed = True


class LabelOps(object):

    def __init__(self, label_ops, project):
        self.label_ops_arr = label_ops
        self.label_ops = {l.name: l for l in label_ops}
        self.names = {l.name: i for i, l in enumerate(label_ops)}
        self.labels = list(set(sorted(l.label for l in label_ops)))
        self.labels_idx = {l: i for i, l in enumerate(self.labels)}
        self.project = project

    def _check_results(self, regions_to_labels):
        result = lg.get_regions_by_ids_with_data(list(regions_to_labels.keys()))
        out = []
        for r, label in zip(result, regions_to_labels.values()):
            d = r['data']
            d['task'] = r['region']['task']
            d['label'] = label
            out.append(d)
        return pd.DataFrame.from_records(out)

    def apply(self):
        pattern_results = {}
        all_ids = set()
        for label_op in self.label_ops.values():
            res = label_op.pattern.retrieve()
            lop_ids = set()
            for name, ids in res.items():
                lop_ids |= set(ids)
            pattern_results[label_op.name] = list(lop_ids)
            all_ids |= lop_ids

        all_ids = list(sorted(all_ids))
        all_ids_map = {ii: i for i, ii in enumerate(all_ids)}
        num_examples = len(all_ids)
        label_mtx = np.zeros(shape=(num_examples, len(self.labels)), dtype=int)
        label_mtx.fill(-1)

        for name, ids in pattern_results.items():
            j = self.names[name]
            ids_mapped = [all_ids_map[i] for i in ids]
            lop = self.label_ops[name]
            label_idx = self.labels_idx[lop.label]
            label_mtx[ids_mapped, j] = label_idx

        lfa = LFAnalysis(label_mtx)
        coverage = lfa.label_coverage()
        conflict = lfa.label_conflict()

        lops_coverages = lfa.lf_coverages()
        lops_conflicts = lfa.lf_conflicts()
        lop_stats = []
        for j, (cov, con) in enumerate(zip(lops_coverages, lops_conflicts)):
            lop = self.label_ops_arr[j].name
            lop_stats.append({'name': lop, 'coverage': cov, 'conflict': con})

        majority_model = MajorityLabelVoter()
        preds = majority_model.predict(L=label_mtx)

        regions_to_labels = {}
        for i, pred_label_idx in enumerate(preds):
            regions_to_labels[all_ids[i]] = self.labels[pred_label_idx]

        view = self._check_results(regions_to_labels)

        return {
            'conflict': conflict,
            'coverage': coverage,
            'predictions': regions_to_labels,
            'aggregated': view,
            'stats': lop_stats
        }

    def commit(self, result):
        regions = lg.get_regions_by_ids(list(result['predictions'].keys()))
        for region, label in zip(regions, result['predictions'].values()):
            if region['start'] == -1 and region['end'] == -1:
                self.project.create_predictions([{
                    'task': region['task'],
                    'result': 'label',
                    'score': 1.0
                }])

    @classmethod
    def from_yaml(cls, filename, project):
        with open(filename) as f:
            label_ops = yaml.load(f, Loader=yaml.FullLoader)
        lops = []
        for label_op in label_ops:
            pattern = None
            if label_op['pattern']['type'] == 'Regex':
                pattern = Regex(query=label_op['pattern']['query'])
            elif label_op['pattern']['type'] == 'Entities':
                pattern = Entities(query=label_op['pattern']['query'])
            if not pattern:
                continue
            lops.append(LabelOp(name=label_op['name'], pattern=pattern, label=label_op['label']))
        return cls(lops, project)

