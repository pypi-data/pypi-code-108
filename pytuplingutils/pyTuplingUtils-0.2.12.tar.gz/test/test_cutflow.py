#!/usr/bin/env python3
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Fri May 01, 2020 at 07:03 PM +0800

import unittest
import os.path as osp

from context import pyTuplingUtils as ptu
from context import pwd

rule = ptu.cutflow.CutflowRule
cfg = ptu.cutflow.CutflowGen
evaluator = ptu.boolean.eval.BooleanEvaluator


class CutflowTest(unittest.TestCase):
    ntp_path = osp.join(pwd, '../samples/sample.root')
    tree = 'TupleB0/DecayTree'
    exe = evaluator(ntp_path, tree)

    def test_cutflow_canonical(self):
        rules = [
            rule('muplus_L0Global_TIS & (Y_L0Global_TIS | Dst_2010_minus_L0HadronDecision_TOS)', key='L0'),
            rule('Kplus_Hlt1Phys_Dec', key='Hlt1'),
            rule('D0_Hlt2XcMuXForTauB2XcMuDecision_Dec', key='Hlt2'),
            rule('muplus_isMuon & muplus_PIDmu > 2', r'$\mu$ PID'),
            rule('Y_ISOLATION_BDT < 0.15', r'$\text{IsoBDT}_{\Upsilon(\text{4s})} < 0.15$'),
            rule('Y_M < 5280', r'$m_{\Upsilon(\text{4s})} < 5280$'),
        ]

        result = cfg(self.ntp_path, self.tree, rules, 2333).do()

        self.assertEqual(result['L0']['input'], 2333)
        self.assertEqual(result['L0']['output'], 176)
        self.assertEqual(result['muplus_isMuon & muplus_PIDmu > 2']['input'], 176)
        self.assertEqual(result['muplus_isMuon & muplus_PIDmu > 2']['output'], 167)
        self.assertEqual(result['muplus_isMuon & muplus_PIDmu > 2']['name'], r'$\mu$ PID')
        self.assertEqual(result['Y_M < 5280']['input'], 119)
        self.assertEqual(result['Y_M < 5280']['output'], 119)

    def test_cutflow_exotic(self):
        rules = [
            rule('Dst_2010_minus_L0HadronDecision_TOS'),
            rule('Dst_2010_minus_L0HadronDecision_TOS & Y_L0MuonDecision_TIS', compare_to=0, explicit=True),
            rule('Dst_2010_minus_L0HadronDecision_TOS & Y_L0ElectronDecision_TIS', compare_to=0, explicit=True),
        ]

        result = cfg(self.ntp_path, self.tree, rules, 2333).do()

        self.assertEqual(result['Dst_2010_minus_L0HadronDecision_TOS']['input'], 2333)
        self.assertEqual(result['Dst_2010_minus_L0HadronDecision_TOS']['output'], 85)
        self.assertEqual(result['Dst_2010_minus_L0HadronDecision_TOS & Y_L0MuonDecision_TIS']['input'], 85)
        self.assertEqual(result['Dst_2010_minus_L0HadronDecision_TOS & Y_L0MuonDecision_TIS']['output'], 8)
        self.assertEqual(result['Dst_2010_minus_L0HadronDecision_TOS & Y_L0ElectronDecision_TIS']['input'], 85)
        self.assertEqual(result['Dst_2010_minus_L0HadronDecision_TOS & Y_L0ElectronDecision_TIS']['output'], 10)


if __name__ == '__main__':
    unittest.main()
