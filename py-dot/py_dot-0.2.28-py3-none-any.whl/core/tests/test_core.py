import unittest

from py_dot.core import casting


class TestCore(unittest.TestCase):
    def test_casting(self):
        self.assertEqual(casting('true'), True)
        self.assertEqual(casting('True'), True)
        self.assertEqual(casting('TRUE'), True)
        self.assertEqual(casting('tRUe'), 'tRUe')
        self.assertEqual(casting('false'), False)
        self.assertEqual(casting('False'), False)
        self.assertEqual(casting('FALSE'), False)
        self.assertEqual(casting('fALSe'), 'fALSe')
        self.assertEqual(casting('null'), None)
        self.assertEqual(casting('NULL'), None)
        self.assertEqual(casting('undefined'), None)
        self.assertEqual(casting('Nope'), 'Nope')
        self.assertEqual(casting('1'), 1)
        self.assertEqual(casting('1.1'), 1.1)
        self.assertEqual(casting(True), True)
        self.assertEqual(casting(False), False)
        self.assertEqual(casting(None), None)





