# pylint: disable=C0103,W0212,C0111,C0325
import os
import unittest
import threading
from murano_client.client import MuranoClient
from exoedge.config_io import ConfigIO
from exoedge.config_applications import ConfigApplications

test_dir = os.path.dirname(os.path.abspath(__file__))


class TestConfigIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        print("setup for test: {}".format(self.id().split('.')[-1]))

    def tearDown(self):
        print("teardown for test: {}".format(self.id().split('.')[-1]))

    def test_no_local_config(self):
        c = ConfigIO(
            device=MuranoClient(
                murano_host='https://random.m2.exosite.io/',
                watchlist=['config_io'],
            )
        )
        self.assertIsNotNone(c)
        self.assertFalse(c.channels)
        self.assertEqual(c.config_file, 'config_io.json')

    def test_no_device(self):
        # config objects need MuranoClient objects.
        with self.assertRaises(AssertionError):
            ConfigIO()

    def test_default_config_file(self):
        c = ConfigIO(
            device=MuranoClient(
                murano_host='https://random.m2.exosite.io/',
                watchlist=['config_io'],
                murano_id='MYMURANOID'
            )
        )
        self.assertEqual(c.config_file, 'config_io.json')

    def test_complete_config_file(self):
        path_to_file = os.path.join(test_dir, 'assets/complete-channel-config.json')
        c = ConfigIO(
            device=MuranoClient(
                murano_host='https://random.m2.exosite.io/',
                watchlist=['config_io'],
                murano_id='MYMURANOID'
            ),
            config_io_file=path_to_file
        )
        self.assertEqual(c.config_file, path_to_file)

    def test_parse_name(self):
        c = ConfigIO(
            device=MuranoClient(
                murano_host='https://random.m2.exosite.io/',
                watchlist=['config_io'],
                murano_id='MYMURANOID'
            ),
            config_io_file={}
        )
        self.assertEqual(c.parse_name('Modbus_TCP'),
                         ('exoedge_modbus', 'ModbusExoEdgeSource'))
        self.assertEqual(c.parse_name('Modbus_RTU'),
                         ('exoedge_modbus', 'ModbusExoEdgeSource'))
        self.assertEqual(c.parse_name('CANOpen'),
                         ('exoedge_canopen', 'CanopenExoEdgeSource'))


class TestConfigApplications(unittest.TestCase):
    def test_no_local_config(self):
        c = ConfigApplications(
            device=MuranoClient(
                murano_host='https://random.m2.exosite.io/',
                watchlist=['config_io'],
            )
        )
        self.assertIsNotNone(c)
        self.assertEqual(c.config_file, 'config_applications.json')

    def test_no_device(self):
        # config objects need MuranoClient objects.
        with self.assertRaises(AssertionError):
            ConfigApplications()

    def test_default_config_file(self):
        c = ConfigApplications(
            device=MuranoClient(
                murano_host='https://random.m2.exosite.io/',
                watchlist=['config_io'],
                murano_id='MYMURANOID'
            )
        )
        self.assertEqual(c.config_file, 'config_applications.json')

    def test_complete_config_file(self):
        path_to_file = os.path.join(test_dir, 'assets/complete-channel-config.json')
        c = ConfigApplications(
            device=MuranoClient(
                murano_host='https://random.m2.exosite.io/',
                watchlist=['config_io'],
                murano_id='MYMURANOID'
            ),
            config_applications_file=path_to_file
        )
        self.assertEqual(c.config_file, path_to_file)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
