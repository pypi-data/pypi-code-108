#!/usr/bin/env python3
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Mon May 24, 2021 at 10:06 PM +0200

import uproot

from dataclasses import dataclass
from typing import Union, Optional
from numpy import sum
from numpy import logical_and as AND
from copy import deepcopy

from pyTuplingUtils.boolean.eval import BooleanEvaluator
from pyTuplingUtils.utils import extract_uid
from pyTuplingUtils.io import read_branches


def cutflow_uniq_events_outer(
        ntp, tree, run_branch='runNumber', event_branch='eventNumber'):
    run, event = read_branches(ntp, tree, (run_branch, event_branch))

    def inner(ntp_i, tree_i, arr):
        return extract_uid(ntp_i, tree_i, conditional=arr,
                           run_array=run, event_array=event)[3]

    return inner


@dataclass
class CutflowRule:
    cond: str = 'true'
    name: Optional[str] = None
    compare_to: Union[str, int] = 'r:-1'
    explicit: bool = False
    key: Optional[str] = None


class CutflowGen:
    def __init__(self, ntp_path, tree, rules, init_num, **kwargs):
        self.rules = self.strip_multiline_str(rules)
        self.init_num = init_num

        self.ntp = uproot.open(ntp_path)
        self.tree = tree
        self.exe = BooleanEvaluator(self.ntp, tree, **kwargs)

        self.debug_raw_output = []

    def do(self, output_regulator=lambda ntp, tree, arr: sum(arr)):
        ref = {}
        result = {}

        for idx, r in enumerate(self.rules):
            prev_idx = self.find_idx(idx, r.compare_to)

            # If the 'output' entry does not exist, use the default initial
            # number of events/candidates.
            try:
                prev_output = ref[self.rules[prev_idx].cond]['output']
                prev_raw_output = ref[self.rules[prev_idx].cond]['raw_output']
            except Exception:
                prev_output = self.init_num
                prev_raw_output = True

            # Note that 'raw_output' is an array of boolean
            raw_output = self.exe.eval(r.cond)
            if not r.explicit:
                raw_output = AND(prev_raw_output, raw_output)
            self.debug_raw_output.append(raw_output)

            # Here, 'output' is a number
            if True in raw_output:
                output = output_regulator(self.ntp, self.tree, raw_output)
            else:
                output = 0

            cut_result = {'input': prev_output, 'output': output}

            if r.name:
                cut_result['name'] = r.name

            if r.key:
                result[r.key] = cut_result
            else:
                result[r.cond] = cut_result

            # Include the raw array of boolean in the reference.
            ref_cut_result = deepcopy(cut_result)
            ref_cut_result['raw_output'] = raw_output
            ref[r.cond] = ref_cut_result

        return result

    @staticmethod
    def find_idx(ref_idx, raw_idx):
        if isinstance(raw_idx, str):  # relative index
            _, idx = raw_idx.split(':')
            idx = ref_idx + int(idx)
        else:
            idx = int(raw_idx)

        return idx

    @staticmethod
    def strip_multiline_str(rules):
        result = []
        for r in rules:
            stripped_rule = CutflowRule(
                r.cond.replace('\n', ' '),
                r.name, r.compare_to, r.explicit, r.key
            )
            result.append(stripped_rule)
        return result
