# pylint: disable=C0103,W0602,C0325,C0301,C0111
import os
import unittest
import json
import pureyaml
from exoedge import channel

test_dir = os.path.dirname(os.path.abspath(__file__))


class TestChannel(unittest.TestCase):
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


    def test_001_channel_constructor(self):
        c = channel.Channel(
            **json.load(open(os.path.join(test_dir, 'assets/complete-channel-config.json')))
        )
        self.assertIsNotNone(c)

    def test_002_channel_roch(self):
        ch_conf = json.load(
            open(
                os.path.join(test_dir, 'assets/complete-channel-config.json'))
        )
        print(ch_conf)
        ch_conf['protocol_config']['report_on_change'] = True
        ch_conf['protocol_config']['report_on_change_tolerance'] = 0.1
        c = channel.Channel(**ch_conf)
        self.assertIsNotNone(c.ROCH.filter_data([channel.Sample(1.0)], 1.2)[-1].data)

    def test_003_channel_roch(self):
        ch_conf = json.load(
            open(
                os.path.join(test_dir, 'assets/complete-channel-config.json'))
        )
        print(ch_conf)
        ch_conf['protocol_config']['report_on_change'] = True
        ch_conf['protocol_config']['report_on_change_tolerance'] = 0.1
        c = channel.Channel(**ch_conf)
        self.assertIsNone(c.ROCH.filter_data([channel.Sample(1.0)], 1.02)[-1].data)


def main():
    unittest.main()

if __name__ == "__main__":
    main()
