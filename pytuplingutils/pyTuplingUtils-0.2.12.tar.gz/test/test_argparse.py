#!/usr/bin/env python3
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Sun Jun 13, 2021 at 12:38 AM +0200

import unittest

from context import pyTuplingUtils as ptu
from context import pwd


class SplitNtpTreeTest(unittest.TestCase):
    def test_split(self):
        ntp_tree = 'a/b/c/d.root/TupleB0/DecayTree'
        ntp, tree = ptu.argparse.split_ntp_tree(ntp_tree)

        assert ntp == 'a/b/c/d.root'
        assert tree == 'TupleB0/DecayTree'
