# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
# Discover and run doctests, report results alongside other unittest results.

from doctest import DocTestSuite
from unittest import TestSuite


def netconf_module(name):
    """Construct a module name relative to __name__."""
    return '.'.join(__name__.split('.')[:-2] +
                    [name])


def load_tests(*args):
    """Wrap module doctests into a unittest TestSuite.

    Called automatically by unittest.
    """
    suite = TestSuite()
    suite.addTests(DocTestSuite(netconf_module('rpcbuilder')))
    return suite
