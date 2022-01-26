# pylint: disable=C0103,W0602,C0325,C0301,C0111
import os
import unittest
import json
from exoedge.config_io import ConfigIO
from exoedge.config_applications import ConfigApplications
from murano_client.client import MuranoClient

test_dir = os.path.dirname(os.path.abspath(__file__))


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    @classmethod
    def tearDownClass(cls):
        pass
    def setUp(self):
        self.test_name = self.id().split('.')[-1]
        self.test_config_file = os.path.join(test_dir, self.test_name)
        with open(self.test_config_file, 'w'):
            pass
        print("setup for test: {}".format(self.test_name))

    def tearDown(self):
        print("teardown for test: {}".format(self.test_name))
        os.unlink(self.test_config_file)

    def test_001_config_io_default(self):

        config_io = ConfigIO(
            device=MuranoClient(
                murano_host="https://dne.m2.exosite.io/",
                watchlist=['data_out']
            )
        )
        self.assertEqual(config_io.config_file, 'config_io.json')

    def test_002_config_io_configured(self):

        config_io = ConfigIO(
            device=MuranoClient(
                murano_host="https://dne.m2.exosite.io/",
                watchlist=['data_out']
            ),
            config_io_file='/custom/path.json'
        )
        self.assertEqual(config_io.config_file, '/custom/path.json')

    def test_003_set_config_verify_file_sync(self):

        config_io = ConfigIO(
            device=MuranoClient(
                murano_host="https://dne.m2.exosite.io/",
                watchlist=['data_out']
            ),
            config_io_file=self.test_config_file
        )
        self.assertEqual(config_io.config_file, self.test_config_file)

        config = json.load(open(os.path.join(test_dir, 'assets/complete-channel-config.json')))
        config_io.set_config(config)
        self.assertEqual(config_io.config, config)
        self.assertEqual(config, json.load(open(self.test_config_file, 'r')))







    def test_010_config_applications_default(self):

        config_applications = ConfigApplications(
            device=MuranoClient(
                murano_host="https://dne.m2.exosite.io/",
                watchlist=['data_out']
            )
        )
        self.assertEqual(config_applications.config_file, 'config_applications.json')

    def test_020_config_applications_configured(self):

        config_applications = ConfigApplications(
            device=MuranoClient(
                murano_host="https://dne.m2.exosite.io/",
                watchlist=['data_out']
            ),
            config_applications_file='/custom/path.json'
        )
        self.assertEqual(config_applications.config_file, '/custom/path.json')

    def test_030_set_config_verify_file_sync(self):

        config_applications = ConfigApplications(
            device=MuranoClient(
                murano_host="https://dne.m2.exosite.io/",
                watchlist=['data_out']
            ),
            config_applications_file=self.test_config_file
        )
        self.assertEqual(config_applications.config_file, self.test_config_file)

        config = json.load(open(os.path.join(test_dir, 'assets/complete-channel-config.json')))
        config_applications.set_config(config)
        self.assertEqual(config_applications.config, config)
        self.assertEqual(config, json.load(open(self.test_config_file, 'r')))








def main():
    unittest.main()

if __name__ == "__main__":
    main()
