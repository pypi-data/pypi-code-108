import unittest

from cc_py_commons.utils.case_conversion import camelize, camel_to_snake_case, to_camel_case, to_snake_case

class TestCaseConversion(unittest.TestCase):

  def test_camelize(self):
    input = 'test_input'
    result = camelize(input)
    self.assertEqual('testInput', result)

  def test_camel_to_snake_case(self):
    input = 'testInput'
    result = camel_to_snake_case(input)
    self.assertEqual('test_input', result)

  def test_to_camel_case(self):
    input = {
      'test_key': 'test_value'
    }
    result = to_camel_case(input)
    self.assertFalse('test_key' in result)
    self.assertTrue('testKey' in result)

  def test_to_snake_case(self):
    input = {
      'testKey': 'test_value'
    }
    result = to_snake_case(input)
    self.assertFalse('testKey' in result)
    self.assertTrue('test_key' in result)
