#!/usr/bin/env python3
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Mon Jun 14, 2021 at 03:35 AM +0200

import unittest

from context import pyTuplingUtils as ptu
from context import pwd


class FilterKwargsFuncTest(unittest.TestCase):
    @staticmethod
    def sample_func(a=1, b=2):
        pass

    def test_args(self):
        kwargs = {'a': 2, 'c': 3, 'd': 4}
        kw_known, kw_rest = ptu.plot.filter_kwargs_func(
            kwargs, self.sample_func)

        assert kw_known == {'a': 2}
        assert kw_rest == {'c': 3, 'd': 4}


class AxStyleTest(unittest.TestCase):
    def test_ax_errorbar_all_known_kw(self):
        assert ptu.plot.ax_add_args_errorbar('a', 'black', marker='x') == {
            'label': 'a',
            'ls': 'none',
            'color': 'black',
            'marker': 'x',
            'markeredgecolor': 'none',
            'yerr': None
        }

    def test_ax_errorbar_some_unknown_kw(self):
        assert ptu.plot.ax_add_args_errorbar(
            'a', 'black', marker='x', test='test') == {
            'label': 'a',
            'ls': 'none',
            'color': 'black',
            'marker': 'x',
            'markeredgecolor': 'none',
            'yerr': None,
            'test': 'test'
        }
