import unittest
import os
import warnings
from bwgds.berryworld.config_loader import ConfigLoader

warnings.filterwarnings('ignore')


class TestConfigLoader(unittest.TestCase):

    def test_config_loader(self):
        value = 'value_1'
        config = ConfigLoader()
        os.environ['Test_1'] = value
        test = config.get('Test_1')
        self.assertEqual(value, test)


if __name__ == '__main__':
    TestConfigLoader().test_config_loader()