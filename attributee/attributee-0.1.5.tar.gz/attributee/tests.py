
import unittest

from attributee import Attributee, Include, Nested, Unclaimed
from attributee.primitives import Integer

class Tests(unittest.TestCase):

    def test_nested(self):
        
        class A(Attributee):

            a = Integer()
            b = Integer()

        class B(Attributee):

            nested = Nested(A)
            c = Integer()

        b = B(nested=dict(a=1, b=2), c=3)

        self.assertEqual(getattr(b, "c", 0), 3)
        self.assertEqual(getattr(b.nested, "a", 0), 1)
        self.assertEqual(getattr(b.nested, "b", 0), 2)

    def test_include(self):
        
        class A(Attributee):

            a = Integer()
            b = Integer()

        class B(Attributee):

            inner = Include(A)
            c = Integer()

        b = B(a=1, b=2, c=3)

        self.assertEqual(getattr(b, "c", 0), 3)
        self.assertEqual(getattr(b.inner, "a", 0), 1)
        self.assertEqual(getattr(b.inner, "b", 0), 2)

    def test_unclaimed(self):
        
        class A(Attributee):

            a = Integer()
            b = Integer()

            rest = Unclaimed()

        a = A(a=1, b=2, c=3, d=4)

        self.assertEqual(getattr(a, "a", 0), 1)
        self.assertEqual(getattr(a, "b", 0), 2)
        self.assertEqual(a.rest.get("c", 0), 3 )
        self.assertEqual(a.rest.get("d", 0), 4 )
