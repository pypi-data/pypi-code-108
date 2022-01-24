from __future__ import annotations
import json, uuid, os, re
import datetime as dt

from typing import List
from collections import defaultdict
from schema.insight_engine_request import HistoryClaim
from fhir.resources.claim import Claim

from klee.files import read_json
from klee.internal import log

_claim_re = re.compile(r"(?:(CLUE|CUE)(\d?))?[_-]?(OCL|OC)?(\d?[a-zA-Z]?)[_-](\d+[YN]).json")

class ClaimsDirectory:
    def __init__(self, claims_folder):
        self.all_claims, self.claims = {}, {}
        self.history = defaultdict(list)
        self.location = claims_folder

    def load_claims(self):
        for filename in self.list_json:
            tc = self.new_claim(filename)
            self.all_claims[tc.file_id] = tc
            if tc.is_history:
                self.history[tc.label_id].append(tc)
            else:
                self.claims[tc.label_id] = tc
                tc.shuffle_patient(tc.uuid)
        # sync tx_ids on history
        for label in self.history:
            for historic in self.history[label]:
                log.info("schema matching history: %s from %s to %s", label, historic.file_id, historic.label_id)
                if historic.label_id in self.claims:
                    parent = self.claims[historic.label_id]
                    historic.shuffle_patient(parent.uuid)
                    historic.tx_id = parent.tx_id
                else:
                    log.warning('note: for nodes with multiple test cases, ensure that OC/OCL indexes are 2 wide')
                    log.warning('warning: loose OCL file, unknown behavior, ignoring file')
                    log.warning('file: %s', historic.file_id)

    def new_claim(self, filename: str) -> KleeTestClaim:
        return KleeTestClaim(self, filename)

    def claim_by_file(self, filename: str) -> KleeTestClaim:
        file_description = _claim_re.findall(filename)[0]
        file_id = "-".join(x for x in file_description if x)
        return self.all_claims[file_id]

    @property
    def list_json(self) -> List[str]:
        # noinspection PyTypeChecker
        return [file for file in os.listdir
            (self.location) if file.endswith(".json")]

class KleeTestClaim:
    def __init__(self, claims_dir: ClaimsDirectory, filename: str):
        self.claims_dir, self.time = claims_dir, dt.datetime.utcnow().timestamp()
        # init vars
        main_type, idx_1, ex_type, idx_2, self.node_id = \
            file_description = _claim_re.findall(filename)[0]

        self.index = "-".join(x for x in (idx_1, idx_2) if x)
        self.type = "-".join(x for x in (main_type, ex_type) if x)
        # multiple tests per node support {leaf-idx}
        self.rel_idx = idx_1 if main_type else idx_2[:-1]
        self.label_id = "-".join(x for x in (self.node_id, self.rel_idx) if x)
        # unique claim/file id
        self.file_id: str = "-".join(x for x in file_description if x)
        self.claim_json = read_json(os.path.join(self.claims_dir.location, filename))
        self.claim_json['id'] = f'{self.file_id}-{self.time}'
        self.tx_id = 'TX.' + self.claim_json['id']
        self.uuid = str(uuid.uuid4())

    @property
    def fhir_claim(self) -> Claim:
        return Claim.parse_obj(self.claim_json)

    @property
    def is_history(self) -> bool:
        return self.type in ('OCL', 'OC')

    @property
    def schema_history(self) -> List[HistoryClaim]:
        return self.compose_history(self.claims_dir.history[self.label_id])

    def compose_history(self, claims: List[KleeTestClaim]) -> List[HistoryClaim]:
        results = []
        for ix, other in enumerate(claims, 1):
            other.shuffle_patient(self.uuid)
            # other.claim_json['id'] = self.claim_json['id'] + f'-{ix}'
            hc = HistoryClaim(claim = other.fhir_claim, transaction_id = self.tx_id)
            results.append(hc)
        return results

    def shuffle_patient(self, member_id):
        queue = {}

        for item in self.claim_json['contained']:
            if item['resourceType'] == 'Patient':
                old = item['id']; ix = old.split('-')[-1]
                queue[old] = f"Member-{member_id}-{ix}"

        text = json.dumps(self.claim_json)
        for old, new in queue.items():
            text = text.replace(old, new)

        self.claim_json = json.loads(text)
