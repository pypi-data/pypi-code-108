import os
import unittest2 as unittest
import pandas as pd

from yangsuite.paths import set_base_path
from yscoverage.dataset import dataset_for_yangset
from yscoverage.mapcli import ConfigXML


def get_fixture(category, name):
    fixturedir = os.path.join(os.path.dirname(__file__), 'fixtures')
    fixture = os.path.join(fixturedir, category, name)
    return open(fixture).read()


class TestMapCli(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.xml = get_fixture('rpc', 'ddmi-2-9500.edit.cfg')
        cls.cli = get_fixture('cli', 'ddmi-2-9500.cfg')
        set_base_path('/Users/miott/ysuite/install/data')

    def test_get_endpoint(self):
        breakpoint()
        cfgx = ConfigXML(
            self.cli, self.xml, 'yangsuite-developer+9500-all-17.6'
        )
        end_xml, end_cli = cfgx.get_endpoints()
        print('done')

    def test_match_endpoints(self):
        breakpoint()
        cfgx = ConfigXML(
            self.cli, self.xml, 'yangsuite-developer+9500-all-17.6'
        )
        end_xml, end_cli = cfgx.get_endpoints()
        xml_cli = cfgx.match_endpoints(end_xml, end_cli)
        for xc in xml_cli:
            xpath, cli, namespace = xc
            if cli in cfgx.cli:
                cfgx.cli.remove(cli)
        print('done')

    def test_map_cli(self):
        breakpoint()
        set_base_path('/Users/miott/ysuite/install/data')
        dataset = dataset_for_yangset(
            'yangsuite-developer',
            '9500-all-17.6',
            'Cisco-IOS-XE-native',
            addons=['presence']
        )
        df = pd.DataFrame(
            dataset['data'],
            columns=dataset['header']
        )
        df = df.loc[df['presence'] != '']
        xml = get_fixture('rpc', 'ddmi-2-9500.edit.cfg')
        cli = get_fixture('cli', 'ddmi-2-9500.cfg')
        cfgx = ConfigXML(cli, xml, df)
        end_xml, end_cli = cfgx.get_endpoints()
        xml_cli = cfgx.match_endpoints(end_xml, end_cli)
        processed_cli = []
        for xpc in xp_cli:
            xp, cli, namespace = xpc
            processed_cli.append(cli)
        excluded_cli = []
        for line in cfgx.cli:
            if line not in processed_cli:
                excluded_cli.append(line)
        print('done')
