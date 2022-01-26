#!/usr/bin/python
"""
    test_iters.py                    Nat Goodspeed
    Copyright (C) 2010               Nat Goodspeed

NRG 12/01/10
"""
from __future__ import print_function

import sys
import itertools
import string
import unittest
## import os
## sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from pyng import iters

if sys.version_info[:2] < (2, 4):
    sys.exit("This test requires Python 2.4+ generator expressions")

def expensive(truth, history=[]):
    print("Expensive test returning %s" % truth)
    history.append(truth)
    return truth

class TestIters(unittest.TestCase):
    def setUp(self):
        self.seq = (True, True, False, True, True)
        self.d = dict((l, n) for n, l in enumerate(string.ascii_lowercase))

    def test_string_types(self):
        self.assert_(isinstance("abc", iters.string_types))
        self.assert_(isinstance(u"abc", iters.string_types))
        self.assert_(isinstance(b"abc", iters.string_types))
        self.assertFalse(isinstance(17, iters.string_types))
        self.assertFalse(isinstance([], iters.string_types))

    def test_iterable(self):
        self.assert_(not iters.iterable("abc"))
        self.assert_(not iters.iterable(u"abc"))
        self.assert_(not iters.iterable(17))
        self.assert_(not iters.iterable(3.14))
        self.assert_(iters.iterable((0, 1)))
        self.assert_(iters.iterable([0, 1]))
        self.assert_(iters.iterable(x for x in range(2)))

    def test_sequence(self):
        self.assertEqual(next(iter(iters.sequence("abc"))), "abc")
        self.assertEqual(next(iter(iters.sequence(u"abc"))), u"abc")
        self.assertEqual(next(iter(iters.sequence(b"abc"))), b"abc")
        self.assertEqual(next(iter(iters.sequence(['a', 'b', 'c']))), 'a')

    def test_empty(self):
        self.assertFalse(iters.empty("abc"))
        self.assertFalse(iters.empty(ltr for ltr in "abc"))
        self.assert_(iters.empty(""))
        self.assert_(iters.empty(ltr for ltr in ""))

    def test_all(self):
        print("all(%s):" % (self.seq,))
        # The cool thing about any() and all() is that if you use a generator
        # (in this case a generator expression), you get "short-circuit
        # evaluation" for a dynamic sequence of tests. You only pay for the
        # tests up until the first one at which the outcome can be determined.
        history = []
        result = iters.all(expensive(t, history) for t in self.seq)
        print("all() returns %s" % result)
        self.assert_(not result)
        # Convert both to tuples to blur the difference between containers:
        # we just want to know whether the individual elements are equal.
        # (If either could be a tuple or a list, converting to tuple is
        # slightly cheaper: tuple() of a tuple returns the tuple unchanged,
        # whereas list() of a list returns a new copy of the list.)
        self.assertEqual(tuple(history), tuple(self.seq[:3]))
        self.assert_(not history[-1])

    def test_any(self):
        seq = [(not t) for t in self.seq]
        print("any(%s):" % (seq,))
        history = []
        result = iters.any(expensive(t, history) for t in seq)
        print("any() returns %s" % result)
        self.assert_(result)
        self.assertEqual(tuple(history), tuple(seq[:3]))
        self.assert_(history[-1])

    def test_interleave(self):
        # The classic use case for interleave() is to ensure there are
        # newlines between every line of output. If 'lines' is an iterable of
        # lines without newlines, you can write them to a text file as
        # individual lines with:
        # open(outname, "w").writelines(interleave(lines, itertools.repeat('\n')))
        self.assertEqual(''.join(iters.interleave(string.ascii_lowercase[:5],
                                                  string.ascii_uppercase[:5])),
                         "aAbBcCdDeE")
        self.assertEqual(''.join(iters.interleave(string.ascii_lowercase[:5],
                                                  itertools.repeat('\n'))),
                         "a\nb\nc\nd\ne\n")

    def test_lastflag(self):
        self.assertEqual(list(iters.lastflag("")), [])
        self.assertEqual(list(iters.lastflag(ltr for ltr in "")), [])
        self.assertEqual(list(iters.lastflag("a")), [("a", True)])
        self.assertEqual(list(iters.lastflag(ltr for ltr in "a")), [("a", True)])
        self.assertEqual(list(iters.lastflag("abc")),
                         [("a", False), ("b", False), ("c", True)])
        self.assertEqual(list(iters.lastflag(ltr for ltr in "abc")),
                         [("a", False), ("b", False), ("c", True)])

    def test_subdict(self):
        self.assertEqual(iters.subdict(self.d, "wxyz"), dict(w=22, x=23, y=24, z=25))
        self.assertRaises(KeyError, iters.subdict, self.d, ("w", "x", "y", "ABC"))

    def test_interdict(self):
        self.assertEqual(iters.interdict(self.d, "wxyz"), dict(w=22, x=23, y=24, z=25))
        self.assertEqual(iters.interdict(self.d, ("w", "x", "y", "ABC")),
                         dict(w=22, x=23, y=24))

if __name__ == "__main__":
    unittest.main()
