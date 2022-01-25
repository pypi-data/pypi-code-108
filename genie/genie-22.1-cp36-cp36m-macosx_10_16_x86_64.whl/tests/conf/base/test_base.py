#!/usr/bin/env python

# Import unittest module
import unittest
from unittest.mock import Mock
from ipaddress import IPv4Interface

# And import what's needed
from genie.conf.base import Base, ConfigurableBase

class aClass(Base):
    configurable_attributes = ['a', 'b', 'c', 'd']

class test_base(unittest.TestCase):

    def test_init(self):
        '''Initialize base class'''
        with self.assertRaises(TypeError):
            base = Base()
        base = Base(testbed=Mock())

    def test_config_init(self):
        '''Initialize configurable base class'''
        base = ConfigurableBase(testbed=Mock())
        base.os = 'Fake'
        base.context = 'fake'

        # Make sure it contains the right function
        funcs = ['build_config', 'build_unconfig' ]
        for func in funcs:
            self.assertTrue(hasattr(base, func))
            with self.assertRaises(NotImplementedError):
                getattr(base, func)()

    def test_default_init(self):
        '''Verify it set the configurable_attributes as default None'''

        with self.assertRaises(TypeError):
            cls = aClass()
        cls = aClass(testbed=Mock())

        # Make sure they are not set
        for item in cls.configurable_attributes:
            with self.assertRaises(AttributeError):
                self.assertEqual(getattr(cls, item), None)

    def test_default_init_with_kwargs(self):
        '''Set the configurable_attributes as default None and kwargs are
        set correctly'''

        cls = aClass(testbed=Mock(), e=5, f=7, a=3)

        # Make sure it is set to None
        self.assertEqual(cls.a, 3)
        with self.assertRaises(AttributeError):
            self.assertEqual(cls.b, None)
        with self.assertRaises(AttributeError):
            self.assertEqual(cls.c, None)
        with self.assertRaises(AttributeError):
            self.assertEqual(cls.d, None)
        self.assertEqual(cls.e, 5)
        self.assertEqual(cls.f, 7)

    def test_instances(self):

        tb = Mock()

        class A(Base):
            def __hash__(self):
                return 0

        class B(Base):
            def __hash__(self):
                return 0

        class C(A):
            pass

        class AB(A, B):
            pass

        class X(Base):
            pass

        self.assertCountEqual(A._Base_instances(), [])
        self.assertCountEqual(A._Base_instances(subclasses=False), [])
        self.assertCountEqual(B._Base_instances(), [])
        self.assertCountEqual(B._Base_instances(subclasses=False), [])
        self.assertCountEqual(C._Base_instances(), [])
        self.assertCountEqual(C._Base_instances(subclasses=False), [])
        self.assertCountEqual(AB._Base_instances(), [])
        self.assertCountEqual(AB._Base_instances(subclasses=False), [])

        x = X(testbed=tb)  # Not hashable, never tracked.
        self.assertCountEqual(X._Base_instances(), [])

        a1 = A(testbed=tb)
        self.assertIn(a1, Base._Base_instances())
        self.assertNotIn(a1, Base._Base_instances(subclasses=False))
        self.assertCountEqual(A._Base_instances(), [a1])
        self.assertCountEqual(A._Base_instances(subclasses=False), [a1])
        self.assertCountEqual(B._Base_instances(), [])
        self.assertCountEqual(B._Base_instances(subclasses=False), [])
        self.assertCountEqual(AB._Base_instances(), [])
        self.assertCountEqual(AB._Base_instances(subclasses=False), [])

        a2 = A(testbed=tb)
        b1 = B(testbed=tb)
        self.assertIn(a1, Base._Base_instances())
        self.assertIn(a2, Base._Base_instances())
        self.assertIn(b1, Base._Base_instances())
        self.assertNotIn(a1, Base._Base_instances(subclasses=False))
        self.assertNotIn(a2, Base._Base_instances(subclasses=False))
        self.assertNotIn(b1, Base._Base_instances(subclasses=False))
        self.assertCountEqual(A._Base_instances(), [a1, a2])
        self.assertCountEqual(A._Base_instances(subclasses=False), [a1, a2])
        self.assertCountEqual(B._Base_instances(), [b1])
        self.assertCountEqual(B._Base_instances(subclasses=False), [b1])
        self.assertCountEqual(C._Base_instances(), [])
        self.assertCountEqual(C._Base_instances(subclasses=False), [])
        self.assertCountEqual(AB._Base_instances(), [])
        self.assertCountEqual(AB._Base_instances(subclasses=False), [])

        ab1 = AB(testbed=tb)
        self.assertIn(a1, Base._Base_instances())
        self.assertIn(a2, Base._Base_instances())
        self.assertIn(b1, Base._Base_instances())
        self.assertIn(ab1, Base._Base_instances())
        self.assertNotIn(a1, Base._Base_instances(subclasses=False))
        self.assertNotIn(a2, Base._Base_instances(subclasses=False))
        self.assertNotIn(b1, Base._Base_instances(subclasses=False))
        self.assertNotIn(ab1, Base._Base_instances(subclasses=False))
        self.assertCountEqual(A._Base_instances(), [a1, a2, ab1])
        self.assertCountEqual(A._Base_instances(subclasses=False), [a1, a2])
        self.assertCountEqual(B._Base_instances(), [b1, ab1])
        self.assertCountEqual(B._Base_instances(subclasses=False), [b1])
        self.assertCountEqual(C._Base_instances(), [])
        self.assertCountEqual(C._Base_instances(subclasses=False), [])
        self.assertCountEqual(AB._Base_instances(), [ab1])
        self.assertCountEqual(AB._Base_instances(subclasses=False), [ab1])

        c1 = C(testbed=tb)
        self.assertIn(a1, Base._Base_instances())
        self.assertIn(a2, Base._Base_instances())
        self.assertIn(b1, Base._Base_instances())
        self.assertIn(c1, Base._Base_instances())
        self.assertIn(ab1, Base._Base_instances())
        self.assertNotIn(a1, Base._Base_instances(subclasses=False))
        self.assertNotIn(a2, Base._Base_instances(subclasses=False))
        self.assertNotIn(b1, Base._Base_instances(subclasses=False))
        self.assertNotIn(c1, Base._Base_instances(subclasses=False))
        self.assertNotIn(ab1, Base._Base_instances(subclasses=False))
        self.assertCountEqual(A._Base_instances(), [a1, a2, ab1, c1])
        self.assertCountEqual(A._Base_instances(subclasses=False), [a1, a2])
        self.assertCountEqual(B._Base_instances(), [b1, ab1])
        self.assertCountEqual(B._Base_instances(subclasses=False), [b1])
        self.assertCountEqual(C._Base_instances(), [c1])
        self.assertCountEqual(C._Base_instances(subclasses=False), [c1])
        self.assertCountEqual(AB._Base_instances(), [ab1])
        self.assertCountEqual(AB._Base_instances(subclasses=False), [ab1])

if __name__ == '__main__':
    unittest.main()
