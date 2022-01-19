from schema.insight_engine_request import HistoryClaim

from klee.internal import Structure, log
from klee.cases import InsightEngineTestCase
from klee.plans import LegacyTestPlan
from klee.claims import KleeTestClaim
from klee import files

from typing import List, Dict
from dataclasses import dataclass
import os

@dataclass
class PlanInfo:
    node_list: List[str]
    row_number: int
    cue_file: str
    clue_number: int
    oc_files: List[str]
    # expected_insight: str
    last_node: str
    restkey: str

def read_plan_data(folder: str = '') -> Dict[str, PlanInfo]:
    plan_data, search_dirs = {}, [*Structure.iter_search()]
    # custom dir
    if folder:
        search_dirs.append(folder)

    for directory in search_dirs:
        plan_csv = os.path.join(directory, 'test_plan.csv')
        if os.path.exists(plan_csv):
            for raw_row in files.read_csv(plan_csv, normalize=True):
                row = dict(map(lambda xs: _translate(*xs), raw_row.items()))
                node = row['last_node'] = row['node_list'][-1]
                plan_data[node] = PlanInfo(**row)

    log.debug("plan data: %s", plan_data)
    return plan_data

class MPETestPlan(LegacyTestPlan):
    def init_test_plan(self):
        # noinspection PyAttributeOutsideInit
        self.plan_data: Dict[str, PlanInfo] = read_plan_data()

        for directory in [*Structure.iter_search()]:
            plan_csv = os.path.join(directory, 'test_plan.csv')
            if os.path.exists(plan_csv):
                self.plan_data.update()

    def get_primary_claims(self):
        if not self.plan_data:
            return super().get_primary_claims()

        plan_claims = []
        for key, data in self.plan_data.items():
            if key[-1:] in 'YN':
                try:
                    claim = self.claims_dir.claim_by_file(data.cue_file)
                    plan_claims.append((claim.label_id, claim))
                except IndexError:
                    log.error('mpe_test is unable to locate primary claim: %s', key)
        return plan_claims

    def claim_line(self, claim: KleeTestClaim) -> int:
        info = self.plan_data.get(claim.label_id)
        if info and info.clue_number:
            return info.clue_number
        return super().claim_line(claim)

    def get_history(self, claim: KleeTestClaim) -> List[HistoryClaim]:
        plan, history = self.plan_data.get(claim.label_id), []
        if plan and plan.oc_files:
            oc_claims = [self.claims_dir.claim_by_file(oc) for oc in plan.oc_files]
            history = claim.compose_history(oc_claims)
        return history or super().get_history(claim)

    def get_defense(self, case: InsightEngineTestCase) -> str:
        defense = case.insight.defense
        plan = self.plan_data.get(case.claim.label_id)
        if plan and plan.row_number:
            policy_excerpt = self.insights.get(f'row-{plan.row_number}')
            defense = policy_excerpt.defense or defense
        return defense

    def validate_case(self, case: InsightEngineTestCase) -> bool:
        if self.plan_data:
            return case.claim.label_id in self.plan_data

        return super().validate_case(case)

def _id(x):
    return x

def _split(xs):
    return [x.strip() for x in xs.split(',') if x]

def _int(x, v = 0):
    try:
        return int(x)
    except ValueError:
        return v

plan_fields = {
    "labels": ('node_list', _split),
    "rownumber": ('row_number', _int),
    "cuefilename": ('cue_file', _id),
    "cluenumber": ('clue_number', lambda x: _int(x, 1)),
    "ocfilenames": ('oc_files', _split),
    # "Expected Insight, if parameters": ('expected_insight', _id),
}

def _translate(k, v):
    # print(k, v)
    e, f = plan_fields.get(k, ('restkey', _id))
    return e, f(v)
