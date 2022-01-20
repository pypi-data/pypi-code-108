#!/usr/bin/env python3
"""
TEST.STDLIB.ABSTRACT_TESTLIB.PY -- utility module for common 'abstract' container object tests
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common code for the 'abstract container' types in
plib.stdlib. Code is taken from the seq_tests, list_tests, test_tuple,
and test_list modules in the Python test package; however, not all of the
'standard' sequence type tests are implemented, only those which test
'generic' behaviors that are emulated by the plib classes.
"""

import unittest


# Helper functions to allow us to test subscripting

def getitem_helper(seq, index):
    return seq.__getitem__(index)


def getitem_helper2(seq, index):
    return seq[index]


def setitem_helper(seq, index, value):
    seq.__setitem__(index, value)


def setitem_helper2(seq, index, value):
    seq[index] = value


def delitem_helper(seq, index=None):
    seq.__delitem__(index)


def delitem_helper2(seq, index):
    del seq[index]


# The actual test cases

class ImmutableSequenceTest(unittest.TestCase):
    # The type to be tested
    type2test = None
    
    def test_truth(self):
        self.assertTrue(not self.type2test())
        self.assertTrue(self.type2test([42]))
    
    def test_getitem(self):
        u = self.type2test([0, 1, 2, 3, 4])
        for i in range(len(u)):
            self.assertEqual(u[i], i)
            self.assertEqual(u[int(i)], i)
        for i in range(-len(u), -1):
            self.assertEqual(u[i], len(u) + i)
            self.assertEqual(u[int(i)], len(u) + i)
        self.assertRaises(IndexError, getitem_helper2, u, -len(u) - 1)
        self.assertRaises(IndexError, getitem_helper2, u, len(u))
        self.assertRaises(ValueError, getitem_helper2, u, slice(0, 10, 0))
        
        u = self.type2test()
        self.assertRaises(IndexError, getitem_helper2, u, 0)
        self.assertRaises(IndexError, getitem_helper2, u, -1)
        
        self.assertRaises(TypeError, u.__getitem__)
        
        a = self.type2test([10, 11])
        self.assertEqual(a[0], 10)
        self.assertEqual(a[1], 11)
        self.assertEqual(a[-2], 10)
        self.assertEqual(a[-1], 11)
        self.assertRaises(IndexError, getitem_helper2, u, -3)
        self.assertRaises(IndexError, getitem_helper2, u, 3)
        self.assertRaises(TypeError, getitem_helper2, a, 'x')
    
    def test_getitem_subscript(self):
        a = self.type2test([10, 11])
        self.assertEqual(getitem_helper(a, 0), 10)
        self.assertEqual(getitem_helper(a, 1), 11)
        self.assertEqual(getitem_helper(a, -2), 10)
        self.assertEqual(getitem_helper(a, -1), 11)
        self.assertRaises(IndexError, getitem_helper, a, -3)
        self.assertRaises(IndexError, getitem_helper, a, 3)
        self.assertEqual(getitem_helper(a, slice(0, 1)), self.type2test([10]))
        self.assertEqual(getitem_helper(a, slice(1, 2)), self.type2test([11]))
        self.assertEqual(getitem_helper(a, slice(0, 2)), self.type2test([10, 11]))
        self.assertEqual(getitem_helper(a, slice(0, 3)), self.type2test([10, 11]))
        self.assertEqual(getitem_helper(a, slice(3, 5)), self.type2test([]))
        self.assertRaises(IndexError, getitem_helper, a, -len(a) - 1)
        self.assertRaises(IndexError, getitem_helper, a, len(a))
        self.assertRaises(ValueError, getitem_helper, a, slice(0, 10, 0))
        self.assertRaises(TypeError, getitem_helper, a, 'x')
    
    def test_getslice(self):
        l = [0, 1, 2, 3, 4]
        u = self.type2test(l)
        
        self.assertEqual(u[0:0], self.type2test())
        self.assertEqual(u[1:2], self.type2test([1]))
        self.assertEqual(u[-2:-1], self.type2test([3]))
        self.assertEqual(u[-1000:1000], u)
        self.assertEqual(u[1000:-1000], self.type2test([]))
        self.assertEqual(u[:], u)
        self.assertEqual(u[1:None], self.type2test([1, 2, 3, 4]))
        self.assertEqual(u[None:3], self.type2test([0, 1, 2]))
        
        # Extended slices
        self.assertEqual(u[::], u)
        self.assertEqual(u[::2], self.type2test([0, 2, 4]))
        self.assertEqual(u[1::2], self.type2test([1, 3]))
        self.assertEqual(u[::-1], self.type2test([4, 3, 2, 1, 0]))
        self.assertEqual(u[::-2], self.type2test([4, 2, 0]))
        self.assertEqual(u[3::-2], self.type2test([3, 1]))
        self.assertEqual(u[3:3:-2], self.type2test([]))
        self.assertEqual(u[3:2:-2], self.type2test([3]))
        self.assertEqual(u[3:1:-2], self.type2test([3]))
        self.assertEqual(u[3:0:-2], self.type2test([3, 1]))
        self.assertEqual(u[::-100], self.type2test([4]))
        self.assertEqual(u[100:-100:], self.type2test([]))
        self.assertEqual(u[-100:100:], u)
        self.assertEqual(u[100:-100:-1], u[::-1])
        self.assertEqual(u[-100:100:-1], self.type2test([]))
        self.assertEqual(u[-100:100:2], self.type2test([0, 2, 4]))
        
        # Test extreme cases with long ints
        a = self.type2test([0, 1, 2, 3, 4])
        self.assertEqual(a[-pow(2, 128): 3], self.type2test([0, 1, 2]))
        self.assertEqual(a[3: pow(2, 145)], self.type2test([3, 4]))
    
    def test_contains(self):
        u = self.type2test([0, 1, 2])
        for i in u:
            self.assertTrue(i in u)
        for i in min(u) - 1, max(u) + 1:
            self.assertTrue(i not in u)
        
        self.assertRaises(TypeError, u.__contains__)
    
    def test_contains_fake(self):
        class AllEq:
            # Sequences must use rich comparison against each item
            # (unless "is" is true, or an earlier item answered)
            # So instances of AllEq must be found in all non-empty sequences.
            def __eq__(self, other):
                return True
            
            def __hash__(self):
                raise NotImplemented
        
        self.assertTrue(AllEq() not in self.type2test([]))
        self.assertTrue(AllEq() in self.type2test([1]))
    
    def test_contains_order(self):
        # Sequences must test in-order.  If a rich comparison has side
        # effects, these will be visible to tests against later members.
        # In this test, the "side effect" is a short-circuiting raise.
        class DoNotTestEq(Exception):
            pass
        
        class StopCompares:
            def __eq__(self, other):
                raise DoNotTestEq
        
        checkfirst = self.type2test([1, StopCompares()])
        self.assertTrue(1 in checkfirst)
        checklast = self.type2test([StopCompares(), 1])
        self.assertRaises(DoNotTestEq, checklast.__contains__, 1)
    
    def test_len(self):
        self.assertEqual(len(self.type2test()), 0)
        self.assertEqual(len(self.type2test([])), 0)
        self.assertEqual(len(self.type2test([0])), 1)
        self.assertEqual(len(self.type2test([0, 1, 2])), 3)
    
    def test_minmax(self):
        u = self.type2test([0, 1, 2])
        self.assertEqual(min(u), 0)
        self.assertEqual(max(u), 2)
    
    def test_setitem(self):
        a = self.type2test()
        b = self.type2test([1])
        c = self.type2test([1, 2])
        
        self.assertRaises(TypeError, setitem_helper2, a, 0, 'a')
        self.assertRaises(TypeError, setitem_helper2, b, 0, 'a')
        self.assertRaises(TypeError, setitem_helper2, c, 0, 'a')
        
        self.assertRaises(TypeError, setitem_helper2, a, 'x', 'a')
        self.assertRaises(TypeError, setitem_helper2, b, 'x', 'a')
        self.assertRaises(TypeError, setitem_helper2, c, 'x', 'a')
    
    def test_setslice(self):
        a = self.type2test()
        b = self.type2test([1])
        c = self.type2test([1, 2])
        
        self.assertRaises(TypeError, setitem_helper2, a, slice(0, 1), 'a')
        self.assertRaises(TypeError, setitem_helper2, b, slice(0, 1), 'a')
        self.assertRaises(TypeError, setitem_helper2, c, slice(0, 1), 'a')
        
        self.assertRaises(TypeError, setitem_helper2, a, slice(0, 0), 'a')
        self.assertRaises(TypeError, setitem_helper2, b, slice(0, 0), 'a')
        self.assertRaises(TypeError, setitem_helper2, c, slice(0, 0), 'a')
    
    def test_delitem(self):
        a = self.type2test()
        b = self.type2test([1])
        c = self.type2test([1, 2])
        
        # Need to catch two exceptions here due to weirdness with
        # Python ABC special method handling
        self.assertRaises((TypeError, AttributeError), delitem_helper2, a, 0)
        self.assertRaises((TypeError, AttributeError), delitem_helper2, b, 0)
        self.assertRaises((TypeError, AttributeError), delitem_helper2, c, 0)
    
    def test_delslice(self):
        a = self.type2test()
        b = self.type2test([1])
        c = self.type2test([1, 2])
        
        self.assertRaises((TypeError, AttributeError), delitem_helper2, a, slice(0, 1))
        self.assertRaises((TypeError, AttributeError), delitem_helper2, b, slice(0, 1))
        self.assertRaises((TypeError, AttributeError), delitem_helper2, c, slice(0, 1))
        
        self.assertRaises((TypeError, AttributeError), delitem_helper2, a, slice(0, 0))
        self.assertRaises((TypeError, AttributeError), delitem_helper2, b, slice(0, 0))
        self.assertRaises((TypeError, AttributeError), delitem_helper2, c, slice(0, 0))
    
    def test_comparisons(self):
        l = [0, 1]
        a = self.type2test(l)
        self.assertTrue(a == l)
        self.assertTrue(not (a != l))
        self.assertTrue(a <= l)
        self.assertTrue(not (a < l))
        self.assertTrue(a >= l)
        self.assertTrue(not (a > l))
        
        l = [1, 0]
        self.assertTrue(not (a == l))
        self.assertTrue(a != l)
        self.assertTrue(a <= l)
        self.assertTrue(a < l)
        self.assertTrue(not (a >= l))
        self.assertTrue(not (a > l))
        
        l = [0]
        self.assertTrue(not (a == l))
        self.assertTrue(a != l)
        self.assertTrue(not (a <= l))
        self.assertTrue(not (a < l))
        self.assertTrue(a >= l)
        self.assertTrue(a > l)
        
        l = [0, 1, 2]
        self.assertTrue(not (a == l))
        self.assertTrue(a != l)
        self.assertTrue(a <= l)
        self.assertTrue(a < l)
        self.assertTrue(not (a >= l))
        self.assertTrue(not (a > l))
    
    def test_operators(self):
        a = self.type2test()
        b = self.type2test([1])
        c = self.type2test([1, 2])
        
        def add_helper(x, y):
            return x + y
        
        def mul_helper(x, y):
            return x * y
        
        def imul_helper(x, y):
            x *= y
        
        self.assertRaises(TypeError, add_helper, a, [])
        self.assertRaises(TypeError, add_helper, b, [])
        self.assertRaises(TypeError, add_helper, c, [])
        
        self.assertRaises(TypeError, add_helper, [], a)
        self.assertRaises(TypeError, add_helper, [], b)
        self.assertRaises(TypeError, add_helper, [], c)
        
        self.assertRaises(TypeError, add_helper, a, ())
        self.assertRaises(TypeError, add_helper, b, ())
        self.assertRaises(TypeError, add_helper, c, ())
        
        self.assertRaises(TypeError, add_helper, (), a)
        self.assertRaises(TypeError, add_helper, (), b)
        self.assertRaises(TypeError, add_helper, (), c)
        
        self.assertRaises(TypeError, add_helper, a, "")
        self.assertRaises(TypeError, add_helper, b, "")
        self.assertRaises(TypeError, add_helper, c, "")
        
        self.assertRaises(TypeError, add_helper, "", a)
        self.assertRaises(TypeError, add_helper, "", b)
        self.assertRaises(TypeError, add_helper, "", c)
        
        self.assertRaises(TypeError, mul_helper, a, 1)
        self.assertRaises(TypeError, mul_helper, b, 1)
        self.assertRaises(TypeError, mul_helper, c, 1)
        
        self.assertRaises(TypeError, imul_helper, a, 1)
        self.assertRaises(TypeError, imul_helper, b, 1)
        self.assertRaises(TypeError, imul_helper, c, 1)
        
        self.assertRaises(TypeError, mul_helper, 1, a)
        self.assertRaises(TypeError, mul_helper, 1, b)
        self.assertRaises(TypeError, mul_helper, 1, c)
        
        self.assertRaises(TypeError, mul_helper, a, 1)
        self.assertRaises(TypeError, mul_helper, b, 1)
        self.assertRaises(TypeError, mul_helper, c, 1)
        
        self.assertRaises(TypeError, imul_helper, a, 1)
        self.assertRaises(TypeError, imul_helper, b, 1)
        self.assertRaises(TypeError, imul_helper, c, 1)
        
        self.assertRaises(TypeError, mul_helper, 1, a)
        self.assertRaises(TypeError, mul_helper, 1, b)
        self.assertRaises(TypeError, mul_helper, 1, c)
    
    def test_iadd(self):
        a = self.type2test()
        b = self.type2test([1])
        c = self.type2test([1, 2])
        
        def iadd_helper(x, y):
            x += y
        
        self.assertRaises(TypeError, iadd_helper, a, [])
        self.assertRaises(TypeError, iadd_helper, b, [])
        self.assertRaises(TypeError, iadd_helper, c, [])
        
        self.assertRaises(TypeError, iadd_helper, a, ())
        self.assertRaises(TypeError, iadd_helper, b, ())
        self.assertRaises(TypeError, iadd_helper, c, ())
        
        self.assertRaises(TypeError, iadd_helper, a, "")
        self.assertRaises(TypeError, iadd_helper, b, "")
        self.assertRaises(TypeError, iadd_helper, c, "")
    
    def test_count(self):
        a = self.type2test([0, 1, 2, 0, 1, 2, 0, 1, 2])
        self.assertEqual(a.count(0), 3)
        self.assertEqual(a.count(1), 3)
        self.assertEqual(a.count(3), 0)
        
        self.assertRaises(TypeError, a.count)
        
        class BadExc(Exception):
            pass
        
        class BadCmp:
            def __eq__(self, other):
                if other == 2:
                    raise BadExc()
                return False
        
        self.assertRaises(BadExc, a.count, BadCmp())
    
    def test_index(self):
        u = self.type2test([0, 1])
        self.assertEqual(u.index(0), 0)
        self.assertEqual(u.index(1), 1)
        self.assertRaises(ValueError, u.index, 2)
        
        u = self.type2test([-2, -1, 0, 0, 1, 2])
        self.assertEqual(u.count(0), 2)
        self.assertEqual(u.index(0), 2)
        
        self.assertRaises(TypeError, u.index)
        
        class BadExc(Exception):
            pass
        
        class BadCmp:
            def __eq__(self, other):
                if other == 2:
                    raise BadExc()
                return False
        
        a = self.type2test([0, 1, 2, 3])
        self.assertRaises(BadExc, a.index, BadCmp())
        
        a = self.type2test([-2, -1, 0, 0, 1, 2])
        self.assertEqual(a.index(0), 2)
        
        # This used to seg fault before patch #1005778
        self.assertRaises(ValueError, a.index, None)
    
    def test_reversed(self):
        a = self.type2test(range(20))
        r = reversed(a)
        self.assertEqual(list(r), self.type2test(range(19, -1, -1)))
        self.assertRaises(StopIteration, r.__next__)
        self.assertEqual(list(reversed(self.type2test())),
                         self.type2test())


class FixedLengthSequenceTest(ImmutableSequenceTest):
    
    def test_setitem(self):
        a = self.type2test()
        b = self.type2test([1])
        c = self.type2test([1, 2])
        
        self.assertRaises(IndexError, setitem_helper2, a, 0, 'a')
        self.assertRaises(IndexError, setitem_helper2, a, -1, 'b')
        
        setitem_helper2(b, 0, 'a')
        self.assertTrue(b[0] == 'a')
        self.assertRaises(IndexError, setitem_helper2, b, 1, 'b')
        setitem_helper2(b, -1, 'c')
        self.assertTrue(b[-1] == 'c')
        self.assertRaises(IndexError, setitem_helper2, b, -2, 'd')
        
        setitem_helper2(c, 0, 'a')
        self.assertTrue(c[0] == 'a')
        setitem_helper2(c, 1, 'b')
        self.assertTrue(c[1] == 'b')
        self.assertRaises(IndexError, setitem_helper2, c, 2, 'c')
        setitem_helper2(c, -1, 'd')
        self.assertTrue(c[-1] == 'd')
        setitem_helper2(c, -2, 'e')
        self.assertTrue(c[-2] == 'e')
        self.assertRaises(IndexError, setitem_helper2, c, -3, 'f')
        
        self.assertRaises(TypeError, setitem_helper2, a, 'x', 'a')
        self.assertRaises(TypeError, setitem_helper2, b, 'x', 'a')
        self.assertRaises(TypeError, setitem_helper2, c, 'x', 'a')
    
    def test_setitem_subscript(self):
        a = self.type2test()
        b = self.type2test([1])
        c = self.type2test([1, 2])
        
        self.assertRaises(IndexError, setitem_helper, a, 0, 'a')
        self.assertRaises(IndexError, setitem_helper, a, -1, 'b')
        
        setitem_helper(b, 0, 'a')
        self.assertTrue(b[0] == 'a')
        self.assertRaises(IndexError, setitem_helper, b, 1, 'b')
        setitem_helper(b, -1, 'c')
        self.assertTrue(b[-1] == 'c')
        self.assertRaises(IndexError, setitem_helper, b, -2, 'd')
        
        setitem_helper(c, 0, 'a')
        self.assertTrue(c[0] == 'a')
        setitem_helper(c, 1, 'b')
        self.assertTrue(c[1] == 'b')
        self.assertRaises(IndexError, setitem_helper, c, 2, 'c')
        setitem_helper(c, -1, 'd')
        self.assertTrue(c[-1] == 'd')
        setitem_helper(c, -2, 'e')
        self.assertTrue(c[-2] == 'e')
        self.assertRaises(IndexError, setitem_helper, c, -3, 'f')
        
        self.assertRaises(TypeError, setitem_helper, a, 'x', 'a')
        self.assertRaises(TypeError, setitem_helper, b, 'x', 'a')
        self.assertRaises(TypeError, setitem_helper, c, 'x', 'a')
    
    def test_setitem_list(self):
        a = self.type2test([0, 1])
        a[0] = 0
        a[1] = 100
        self.assertEqual(a, self.type2test([0, 100]))
        a[-1] = 200
        self.assertEqual(a, self.type2test([0, 200]))
        a[-2] = 100
        self.assertEqual(a, self.type2test([100, 200]))
        self.assertRaises(IndexError, setitem_helper2, a, -3, 200)
        self.assertRaises(IndexError, setitem_helper2, a, 2, 200)
        
        a = self.type2test([])
        self.assertRaises(IndexError, setitem_helper2, a, 0, 200)
        self.assertRaises(IndexError, setitem_helper2, a, -1, 200)
        self.assertRaises(TypeError, a.__setitem__)
        
        a = self.type2test([0, 1, 2, 3, 4])
        a[0] = 1
        a[1] = 2
        a[2] = 3
        self.assertEqual(a, self.type2test([1, 2, 3, 3, 4]))
        a[0] = 5
        a[1] = 6
        a[2] = 7
        self.assertEqual(a, self.type2test([5, 6, 7, 3, 4]))
        a[-2] = 88
        a[-1] = 99
        self.assertEqual(a, self.type2test([5, 6, 7, 88, 99]))
        a[-2] = 8
        a[-1] = 9
        self.assertEqual(a, self.type2test([5, 6, 7, 8, 9]))
    
    def test_setitem_subscript_list(self):
        a = self.type2test(range(20))
        self.assertRaises(ValueError, setitem_helper2, a, slice(0, 10, 0), [1, 2, 3])
        self.assertRaises(TypeError, setitem_helper2, a, slice(0, 10), 1)
        self.assertRaises(ValueError, setitem_helper2, a, slice(0, 10, 2), [1, 2])
        a[slice(2, 10, 3)] = [1, 2, 3]
        self.assertEqual(a, self.type2test([0, 1, 1, 3, 4, 2, 6, 7, 3,
                                            9, 10, 11, 12, 13, 14, 15,
                                            16, 17, 18, 19]))
    
    def test_setslice(self):
        l = [0, 1]
        a = self.type2test(l)
        self.assertTrue(a == l)
        
        l2 = [1, 0]
        a[:] = l2[:]
        self.assertTrue(a == l2)
        
        a[:-1] = l[:-1]
        self.assertTrue(a == [0, 0])
        
        a[-1:] = l[-1:]
        self.assertTrue(a == l)
        
        a[:2] = l2[:2]
        self.assertTrue(a == l2)
        
        a[-2:] = l[-2:]
        self.assertTrue(a == l)
        
        a[-2:2] = l2[-2:2]
        self.assertTrue(a == l2)
        
        a[-2:-1] = l[-2:-1]
        self.assertTrue(a == [0, 0])
        
        a[1:2] = l[1:2]
        self.assertTrue(a == l)
        
        a[0:1] = [1]
        self.assertTrue(a == [1, 1])
        
        a[1:2] = [0]
        self.assertTrue(a == l2)
    
    def test_setslice_mismatch(self):
        l = [0, 1]
        a = self.type2test(l)
        
        self.assertRaises(ValueError, setitem_helper, a, slice(0, 1), [0, 1])
        self.assertRaises(ValueError, setitem_helper, a, slice(1, 2), [0, 1])
        
        self.assertRaises(ValueError, setitem_helper, a, slice(0, 1), [])
        self.assertRaises(ValueError, setitem_helper, a, slice(1, 2), [])
        
        self.assertRaises(TypeError, setitem_helper, a, slice(0, 1), 1)
        self.assertRaises(TypeError, setitem_helper, a, slice(1, 2), 1)
        
        self.assertRaises(TypeError, setitem_helper, a, slice(0, 0), [0, 1])
        self.assertRaises(TypeError, setitem_helper, a, slice(1, 1), [0, 1])
        self.assertRaises(TypeError, setitem_helper, a, slice(2, 2), [0, 1])
        self.assertRaises(TypeError, setitem_helper, a, slice(-1, -1), [0, 1])
        self.assertRaises(TypeError, setitem_helper, a, slice(-2, -2), [0, 1])
        
        self.assertRaises(TypeError, setitem_helper, a, slice(0, 0), [0])
        self.assertRaises(TypeError, setitem_helper, a, slice(1, 1), [0])
        self.assertRaises(TypeError, setitem_helper, a, slice(2, 2), [0])
        self.assertRaises(TypeError, setitem_helper, a, slice(-1, -1), [0])
        self.assertRaises(TypeError, setitem_helper, a, slice(-2, -2), [0])
        
        a[0:0] = []
        self.assertTrue(a == l)
        a = l[:]
        a[1:1] = []
        self.assertTrue(a == l)
        a = l[:]
        a[2:2] = []
        self.assertTrue(a == l)
        a = l[:]
        a[-1:-1] = []
        self.assertTrue(a == l)
        a = l[:]
        a[-2:-2] = []
        self.assertTrue(a == l)
        
        self.assertRaises(TypeError, setitem_helper, a, slice(0, 0), 1)
        self.assertRaises(TypeError, setitem_helper, a, slice(1, 1), 1)
        self.assertRaises(TypeError, setitem_helper, a, slice(2, 2), 1)
        self.assertRaises(TypeError, setitem_helper, a, slice(-1, -1), 1)
        self.assertRaises(TypeError, setitem_helper, a, slice(-2, -2), 1)
    
    def test_setslice_mismatch_extended(self):
        l = [0, 1]
        a = self.type2test(l)
        
        self.assertRaises(ValueError, setitem_helper, a, slice(0, 1, 1), [0, 1])
        self.assertRaises(ValueError, setitem_helper, a, slice(1, 2, 1), [0, 1])
        
        self.assertRaises(ValueError, setitem_helper, a, slice(0, 1, 1), [])
        self.assertRaises(ValueError, setitem_helper, a, slice(1, 2, 1), [])
        
        self.assertRaises(TypeError, setitem_helper, a, slice(0, 1, 1), 1)
        self.assertRaises(TypeError, setitem_helper, a, slice(1, 2, 1), 1)
        
        self.assertRaises(TypeError, setitem_helper, a, slice(0, 0, 1), [0, 1])
        self.assertRaises(TypeError, setitem_helper, a, slice(1, 1, 1), [0, 1])
        self.assertRaises(TypeError, setitem_helper, a, slice(2, 2, 1), [0, 1])
        self.assertRaises(TypeError, setitem_helper, a, slice(-1, -1, 1), [0, 1])
        self.assertRaises(TypeError, setitem_helper, a, slice(-2, -2, 1), [0, 1])
        
        self.assertRaises(TypeError, setitem_helper, a, slice(0, 0, 1), [0])
        self.assertRaises(TypeError, setitem_helper, a, slice(1, 1, 1), [0])
        self.assertRaises(TypeError, setitem_helper, a, slice(2, 2, 1), [0])
        self.assertRaises(TypeError, setitem_helper, a, slice(-1, -1, 1), [0])
        self.assertRaises(TypeError, setitem_helper, a, slice(-2, -2, 1), [0])
        
        a[0:0:1] = []
        self.assertTrue(a == l)
        a = l[:]
        a[1:1:1] = []
        self.assertTrue(a == l)
        a = l[:]
        a[2:2:1] = []
        self.assertTrue(a == l)
        a = l[:]
        a[-1:-1:1] = []
        self.assertTrue(a == l)
        a = l[:]
        a[-2:-2:1] = []
        self.assertTrue(a == l)
        
        self.assertRaises(TypeError, setitem_helper, a, slice(0, 0, 1), 1)
        self.assertRaises(TypeError, setitem_helper, a, slice(1, 1, 1), 1)
        self.assertRaises(TypeError, setitem_helper, a, slice(2, 2, 1), 1)
        self.assertRaises(TypeError, setitem_helper, a, slice(-1, -1, 1), 1)
        self.assertRaises(TypeError, setitem_helper, a, slice(-2, -2, 1), 1)
    
    def test_reverse(self):
        a = self.type2test([0])
        a.reverse()
        self.assertEqual(a, self.type2test([0]))
        
        a = self.type2test([0, 1])
        a.reverse()
        self.assertEqual(a, self.type2test([1, 0]))
        
        a = self.type2test([0, 1, 2])
        a.reverse()
        self.assertEqual(a, self.type2test([2, 1, 0]))
        
        a = self.type2test()
        a.reverse()
        self.assertEqual(a, self.type2test())


class MutableSequenceTest(FixedLengthSequenceTest):
    
    def test_index_list(self):
        a = self.type2test([-2, -1, 0, 0, 1, 2])
        a.remove(0)
        self.assertEqual(a, self.type2test([-2, -1, 0, 1, 2]))
    
    def test_index_evil(self):
        # Test modifying the list during index's iteration
        class EvilCmp:
            def __init__(self, victim):
                self.victim = victim
            
            def __eq__(self, other):
                del self.victim[:]
                return False
        
        a = self.type2test()
        a[:] = [EvilCmp(a) for _ in range(100)]
    
    def test_delitem(self):
        a = self.type2test()
        b = self.type2test([1])
        c = self.type2test([1, 2])
        
        self.assertRaises(IndexError, delitem_helper2, a, 0)
        self.assertRaises(IndexError, delitem_helper2, a, -1)
        
        self.assertRaises(IndexError, delitem_helper2, b, 1)
        self.assertRaises(IndexError, delitem_helper2, b, -2)
        delitem_helper2(b, 0)
        self.assertTrue(b == [])
        b = self.type2test([1])
        delitem_helper2(b, -1)
        self.assertTrue(b == [])
        
        self.assertRaises(IndexError, delitem_helper2, c, 2)
        self.assertRaises(IndexError, delitem_helper2, c, -3)
        delitem_helper2(c, 1)
        self.assertTrue(c == [1])
        delitem_helper2(c, 0)
        self.assertTrue(c == [])
        c = self.type2test([1, 2])
        delitem_helper2(c, -1)
        self.assertTrue(c == [1])
        c = self.type2test([1, 2])
        delitem_helper2(c, -2)
        self.assertTrue(c == [2])
        
        self.assertRaises(TypeError, delitem_helper2, a, 'x')
        self.assertRaises(TypeError, delitem_helper2, b, 'x')
        self.assertRaises(TypeError, delitem_helper2, c, 'x')
    
    def test_delitem_subscript(self):
        a = self.type2test()
        b = self.type2test([1])
        c = self.type2test([1, 2])
        
        self.assertRaises(IndexError, delitem_helper, a, 0)
        self.assertRaises(IndexError, delitem_helper, a, -1)
        
        self.assertRaises(IndexError, delitem_helper, b, 1)
        self.assertRaises(IndexError, delitem_helper, b, -2)
        delitem_helper(b, 0)
        self.assertTrue(b == [])
        b = self.type2test([1])
        delitem_helper(b, -1)
        self.assertTrue(b == [])
        
        self.assertRaises(IndexError, delitem_helper, c, 2)
        self.assertRaises(IndexError, delitem_helper, c, -3)
        delitem_helper(c, 1)
        self.assertTrue(c == [1])
        delitem_helper(c, 0)
        self.assertTrue(c == [])
        c = self.type2test([1, 2])
        delitem_helper(c, -1)
        self.assertTrue(c == [1])
        c = self.type2test([1, 2])
        delitem_helper(c, -2)
        self.assertTrue(c == [2])
        
        self.assertRaises(TypeError, delitem_helper, a, 'x')
        self.assertRaises(TypeError, delitem_helper, b, 'x')
        self.assertRaises(TypeError, delitem_helper, c, 'x')
    
    def test_delitem_list(self):
        a = self.type2test([0, 1])
        del a[1]
        self.assertEqual(a, [0])
        del a[0]
        self.assertEqual(a, [])
        
        a = self.type2test([0, 1])
        del a[-2]
        self.assertEqual(a, [1])
        del a[-1]
        self.assertEqual(a, [])
        
        a = self.type2test([0, 1])
        self.assertRaises(IndexError, delitem_helper2, a, -3)
        self.assertRaises(IndexError, delitem_helper2, a, 2)
        
        a = self.type2test([])
        self.assertRaises(IndexError, delitem_helper2, a, 0)
        
        self.assertRaises(TypeError, a.__delitem__)
    
    def test_setslice_mismatch(self):
        l = [0, 1]
        l2 = [1, 0]
        a = self.type2test(l)
        
        a[:2] = l2[:2]
        self.assertTrue(a == l2)
        
        a[-2:] = l[-2:]
        self.assertTrue(a == l)
        
        a[-2:2] = l2[-2:2]
        self.assertTrue(a == l2)
        
        a[-2:-1] = l[-2:-1]
        self.assertTrue(a == [0, 0])
        
        a[1:2] = l[1:2]
        self.assertTrue(a == l)
        
        a[0:1] = [1]
        self.assertTrue(a == [1, 1])
        
        a[1:2] = [0]
        self.assertTrue(a == l2)
        
        a[0:1] = [0, 1]
        self.assertTrue(a == [0, 1, 0])
        a = self.type2test(l2)
        a[1:2] = [0, 1]
        self.assertTrue(a == [1, 0, 1])
        
        a = self.type2test(l2)
        a[0:1] = []
        self.assertTrue(a == [0])
        a = self.type2test(l2)
        a[1:2] = []
        self.assertTrue(a == [1])
        
        a = self.type2test(l2)
        a[0:0] = [0, 1]
        self.assertTrue(a == [0, 1, 1, 0])
        a = self.type2test(l2)
        a[1:1] = [0, 1]
        self.assertTrue(a == [1, 0, 1, 0])
        a = self.type2test(l2)
        a[2:2] = [0, 1]
        self.assertTrue(a == [1, 0, 0, 1])
        a = self.type2test(l2)
        a[-1:-1] = [0, 1]
        self.assertTrue(a == [1, 0, 1, 0])
        a = self.type2test(l2)
        a[-2:-2] = [0, 1]
        self.assertTrue(a == [0, 1, 1, 0])
        
        a = self.type2test(l2)
        a[0:0] = [0]
        self.assertTrue(a == [0, 1, 0])
        a = self.type2test(l2)
        a[1:1] = [0]
        self.assertTrue(a == [1, 0, 0])
        a = self.type2test(l2)
        a[2:2] = [0]
        self.assertTrue(a == [1, 0, 0])
        a = self.type2test(l2)
        a[-1:-1] = [0]
        self.assertTrue(a == [1, 0, 0])
        a = self.type2test(l2)
        a[-2:-2] = [0]
        self.assertTrue(a == [0, 1, 0])
        
        a = self.type2test(l2)
        a[0:0] = []
        self.assertTrue(a == l2)
        a = self.type2test(l2)
        a[1:1] = []
        self.assertTrue(a == l2)
        a = self.type2test(l2)
        a[2:2] = []
        self.assertTrue(a == l2)
        a = self.type2test(l2)
        a[-1:-1] = []
        self.assertTrue(a == l2)
        a = self.type2test(l2)
        a[-2:-2] = []
        self.assertTrue(a == l2)
    
    def test_setslice_mismatch_extended(self):
        l = [0, 1]
        l2 = [1, 0]
        a = self.type2test(l)
        
        a[:2:1] = l2[:2:1]
        self.assertTrue(a == l2)
        
        a[-2::1] = l[-2::1]
        self.assertTrue(a == l)
        
        a[-2:2:1] = l2[-2:2:1]
        self.assertTrue(a == l2)
        
        a[-2:-1:1] = l[-2:-1:1]
        self.assertTrue(a == [0, 0])
        
        a[1:2:1] = l[1:2:1]
        self.assertTrue(a == l)
        
        a[0:1:1] = [1]
        self.assertTrue(a == [1, 1])
        
        a[1:2:1] = [0]
        self.assertTrue(a == l2)
        
        a[0:1:1] = [0, 1]
        self.assertTrue(a == [0, 1, 0])
        a = self.type2test(l2)
        a[1:2:1] = [0, 1]
        self.assertTrue(a == [1, 0, 1])
        
        a = self.type2test(l2)
        a[0:1:1] = []
        self.assertTrue(a == [0])
        a = self.type2test(l2)
        a[1:2:1] = []
        self.assertTrue(a == [1])
        
        a = self.type2test(l2)
        a[0:0:1] = [0, 1]
        self.assertTrue(a == [0, 1, 1, 0])
        a = self.type2test(l2)
        a[1:1:1] = [0, 1]
        self.assertTrue(a == [1, 0, 1, 0])
        a = self.type2test(l2)
        a[2:2:1] = [0, 1]
        self.assertTrue(a == [1, 0, 0, 1])
        a = self.type2test(l2)
        a[-1:-1:1] = [0, 1]
        self.assertTrue(a == [1, 0, 1, 0])
        a = self.type2test(l2)
        a[-2:-2:1] = [0, 1]
        self.assertTrue(a == [0, 1, 1, 0])
        
        a = self.type2test(l2)
        a[0:0:1] = [0]
        self.assertTrue(a == [0, 1, 0])
        a = self.type2test(l2)
        a[1:1:1] = [0]
        self.assertTrue(a == [1, 0, 0])
        a = self.type2test(l2)
        a[2:2:1] = [0]
        self.assertTrue(a == [1, 0, 0])
        a = self.type2test(l2)
        a[-1:-1:1] = [0]
        self.assertTrue(a == [1, 0, 0])
        a = self.type2test(l2)
        a[-2:-2:1] = [0]
        self.assertTrue(a == [0, 1, 0])
        
        a = self.type2test(l2)
        a[0:0:1] = []
        self.assertTrue(a == l2)
        a = self.type2test(l2)
        a[1:1:1] = []
        self.assertTrue(a == l2)
        a = self.type2test(l2)
        a[2:2:1] = []
        self.assertTrue(a == l2)
        a = self.type2test(l2)
        a[-1:-1:1] = []
        self.assertTrue(a == l2)
        a = self.type2test(l2)
        a[-2:-2:1] = []
        self.assertTrue(a == l2)
    
    def test_setslice_list(self):
        l = [0, 1]
        a = self.type2test(l)

        for i in range(-3, 4):
            a[:i] = l[:i]
            self.assertEqual(a, l)
            a2 = a[:]
            a2[:i] = a[:i]
            self.assertEqual(a2, a)
            a[i:] = l[i:]
            self.assertEqual(a, l)
            a2 = a[:]
            a2[i:] = a[i:]
            self.assertEqual(a2, a)
            for j in range(-3, 4):
                a[i:j] = l[i:j]
                self.assertEqual(a, l)
                a2 = a[:]
                a2[i:j] = a[i:j]
                self.assertEqual(a2, a)
        
        aa2 = a2[:]
        aa2[:0] = [-2, -1]
        self.assertEqual(aa2, [-2, -1, 0, 1])
        aa2[0:] = []
        self.assertEqual(aa2, [])
        
        a = self.type2test([1, 2, 3, 4, 5])
        a[:-1] = a[:]  # NOTE: standard Python test uses a{:-1] = a here; is that an error?
        self.assertEqual(a, self.type2test([1, 2, 3, 4, 5, 5]))
        a = self.type2test([1, 2, 3, 4, 5])
        a[1:] = a[:]
        self.assertEqual(a, self.type2test([1, 1, 2, 3, 4, 5]))
        a = self.type2test([1, 2, 3, 4, 5])
        a[1:-1] = a[:]
        self.assertEqual(a, self.type2test([1, 1, 2, 3, 4, 5, 5]))
        
        a = self.type2test([])
        a[:] = tuple(range(10))
        self.assertEqual(a, self.type2test(range(10)))
    
    def test_delslice(self):
        a = self.type2test([0, 1])
        del a[1:2]
        del a[0:1]
        self.assertEqual(a, self.type2test([]))
        
        a = self.type2test([0, 1])
        del a[1:2]
        del a[0:1]
        self.assertEqual(a, self.type2test([]))
        
        a = self.type2test([0, 1])
        del a[-2:-1]
        self.assertEqual(a, self.type2test([1]))
        
        a = self.type2test([0, 1])
        del a[-2:-1]
        self.assertEqual(a, self.type2test([1]))
        
        a = self.type2test([0, 1])
        del a[1:]
        del a[:1]
        self.assertEqual(a, self.type2test([]))
        
        a = self.type2test([0, 1])
        del a[1:]
        del a[:1]
        self.assertEqual(a, self.type2test([]))
        
        a = self.type2test([0, 1])
        del a[-1:]
        self.assertEqual(a, self.type2test([0]))
        
        a = self.type2test([0, 1])
        del a[-1:]
        self.assertEqual(a, self.type2test([0]))
        
        a = self.type2test([0, 1])
        del a[:]
        self.assertEqual(a, self.type2test([]))
    
    def test_slice(self):
        u = self.type2test("spam")
        u[:2] = "h"
        self.assertEqual(u, list("ham"))
    
    def test_extendedslicing(self):
        a = self.type2test([0, 1, 2, 3, 4])
        
        del a[::2]
        self.assertEqual(a, self.type2test([1, 3]))
        a = self.type2test(range(5))
        del a[1::2]
        self.assertEqual(a, self.type2test([0, 2, 4]))
        a = self.type2test(range(5))
        del a[1::-2]
        self.assertEqual(a, self.type2test([0, 2, 3, 4]))
        a = self.type2test(range(10))
        del a[::1000]
        self.assertEqual(a, self.type2test([1, 2, 3, 4, 5, 6, 7, 8, 9]))
        #  assignment
        a = self.type2test(range(10))
        a[::2] = [-1] * 5
        self.assertEqual(a, self.type2test([-1, 1, -1, 3, -1, 5, -1, 7, -1, 9]))
        a = self.type2test(range(10))
        a[::-4] = [10] * 3
        self.assertEqual(a, self.type2test([0, 10, 2, 3, 4, 10, 6, 7, 8, 10]))
        a = self.type2test(range(4))
        a[::-1] = a
        self.assertEqual(a, self.type2test([3, 2, 1, 0]))
        a = self.type2test(range(10))
        b = a[:]
        c = a[:]
        a[2:3] = self.type2test(["two", "elements"])
        b[slice(2, 3)] = self.type2test(["two", "elements"])
        c[2:3:] = self.type2test(["two", "elements"])
        self.assertEqual(a, b)
        self.assertEqual(a, c)
        a = self.type2test(range(10))
        a[::2] = tuple(range(5))
        self.assertEqual(a, self.type2test([0, 1, 1, 3, 2, 5, 3, 7, 4, 9]))
    
    def test_append(self):
        a = self.type2test([])
        a.append(0)
        a.append(1)
        a.append(2)
        self.assertEqual(a, self.type2test([0, 1, 2]))
        
        self.assertRaises(TypeError, a.append)
    
    def test_extend(self):
        a1 = self.type2test([0])
        a2 = self.type2test((0, 1))
        a = a1[:]
        a.extend(a2)
        self.assertEqual(a, self.type2test([0, 0, 1]))
        self.assertEqual(a, self.type2test((0, 0, 1)))
        
        a.extend(self.type2test([]))
        self.assertEqual(a, self.type2test([0, 0, 1]))
        self.assertEqual(a, self.type2test((0, 0, 1)))
        
        a.extend(a[:])
        self.assertEqual(a, self.type2test([0, 0, 1, 0, 0, 1]))
        
        a = self.type2test("spam")
        a.extend("eggs")
        self.assertEqual(a, list("spameggs"))
        
        self.assertRaises(TypeError, a.extend, None)
        
        self.assertRaises(TypeError, a.extend)
    
    def test_iadd(self):
        a1 = self.type2test([0])
        a2 = self.type2test((0, 1))
        a = a1[:]
        a += a2
        self.assertEqual(a, self.type2test([0, 0, 1]))
        self.assertEqual(a, self.type2test((0, 0, 1)))
        
        a += self.type2test([])
        self.assertEqual(a, self.type2test([0, 0, 1]))
        self.assertEqual(a, self.type2test((0, 0, 1)))
        
        a += a[:]
        self.assertEqual(a, self.type2test([0, 0, 1, 0, 0, 1]))
        
        a = self.type2test("spam")
        a += "eggs"
        self.assertEqual(a, list("spameggs"))
    
    def test_insert(self):
        a = self.type2test([0, 1, 2])
        a.insert(0, -2)
        a.insert(1, -1)
        a.insert(2, 0)
        self.assertEqual(a, [-2, -1, 0, 0, 1, 2])
        
        b = a[:]
        b.insert(-2, "foo")
        b.insert(-200, "left")
        b.insert(200, "right")
        self.assertEqual(b, self.type2test(["left", -2, -1, 0, 0, "foo", 1, 2, "right"]))
        
        self.assertRaises(TypeError, a.insert)
    
    def test_pop(self):
        a = self.type2test([-1, 0, 1])
        a.pop()
        self.assertEqual(a, [-1, 0])
        a.pop(0)
        self.assertEqual(a, [0])
        self.assertRaises(IndexError, a.pop, 5)
        a.pop(0)
        self.assertEqual(a, [])
        self.assertRaises(IndexError, a.pop)
        self.assertRaises(TypeError, a.pop, 42, 42)
        a = self.type2test([0, 10, 20, 30, 40])
    
    def test_remove(self):
        a = self.type2test([0, 0, 1])
        a.remove(1)
        self.assertEqual(a, [0, 0])
        a.remove(0)
        self.assertEqual(a, [0])
        a.remove(0)
        self.assertEqual(a, [])
        
        self.assertRaises(ValueError, a.remove, 0)
        
        self.assertRaises(TypeError, a.remove)
        
        class BadExc(Exception):
            pass
        
        class BadCmp:
            def __eq__(self, other):
                if other == 2:
                    raise BadExc()
                return False
        
        a = self.type2test([0, 1, 2, 3])
        self.assertRaises(BadExc, a.remove, BadCmp())
        
        class BadCmp2:
            def __eq__(self, other):
                raise BadExc()
        
        d = self.type2test('abcdefghcij')
        d.remove('c')
        self.assertEqual(d, self.type2test('abdefghcij'))
        d.remove('c')
        self.assertEqual(d, self.type2test('abdefghij'))
        self.assertRaises(ValueError, d.remove, 'c')
        self.assertEqual(d, self.type2test('abdefghij'))
        
        # Handle comparison errors
        d = self.type2test(['a', 'b', BadCmp2(), 'c'])
        e = self.type2test(d)
        self.assertRaises(BadExc, d.remove, 'c')
        for x, y in zip(d, e):
            # verify that original order and values are retained.
            self.assertTrue(x is y)
    
    def test_clear(self):
        a = self.type2test([0, 1, 2])
        a.clear()
        self.assertEqual(a, self.type2test())
        a.clear()
        self.assertEqual(a, self.type2test())
