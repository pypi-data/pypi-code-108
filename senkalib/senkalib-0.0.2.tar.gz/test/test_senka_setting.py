import unittest
from unittest.mock import *
from src.senkalib.senka_setting import SenkaSetting
import os

class TestSenkaSetting(unittest.TestCase):
  def test_get_available_chain(self):
    setting = SenkaSetting({})
    with patch.object(os, 'listdir', new=TestSenkaSetting.mock_listdir):
      chains = setting.get_available_chain()
      self.assertEqual(chains[0], 'bsc')
      self.assertEqual(chains[1], 'osmosis')

  @classmethod
  def mock_listdir(cls, transaction_hash):
    return ['osmosis', 'bsc']

if __name__ == '__main__':
  unittest.main()