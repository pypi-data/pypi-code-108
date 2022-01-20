# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Tests for utility.nconf module."""

import os.path
import unittest2 as unittest
from jinja2 import Template
from mock import patch, MagicMock, PropertyMock
import ncclient.operations
from ncclient import NCClientError
import lxml.etree as et
import json
import copy

from .. import nconf
from ysyangtree import tasks
from yangsuite.paths import set_base_path, get_path
from .utilities import (
    canned_input_data,
    canned_output_str,
    canned_output_data,
    mock_manager,
)


class TestNConf(unittest.TestCase):
    """Tests for utility.nconf module functions."""

    testdir = os.path.join(os.path.dirname(__file__), 'data')

    @classmethod
    def setUpClass(cls):
        """Function called before starting test execution in this class."""
        set_base_path(cls.testdir)
        cls.maxDiff = None

        cls.GET_CONFIG_CFGD = canned_input_data('get_config_ocif.cfgd.json')
        cls.GET_CONFIG_BASIC = {
            'prefix_namespaces': 'always',
            "gentype": "basic",
            "cfgd": cls.GET_CONFIG_CFGD,
        }
        cls.GET_CONFIG_BASIC_MINIMAL = {
            'prefix_namespaces': 'minimal',
            "gentype": "basic",
            "cfgd": cls.GET_CONFIG_CFGD,
        }
        cls.GET_CONFIG_MINIMAL_DEFAULT = {
            "gentype": "basic",
            "cfgd": cls.GET_CONFIG_CFGD,
        }
        cls.GET_CONFIG_SCRIPT = {
            "gentype": "script",
            'prefix_namespaces': 'always',
            "cfg": json.dumps([{'cfgd': cls.GET_CONFIG_CFGD}]),
        }

        cls.GET_RUN = canned_input_data('get_ocif.run.json')

        cls.EDIT_CONFIG_CFGD = canned_input_data('edit_config_ocif.cfgd.json')
        cls.EDIT_VALUE_PREFIXED = canned_input_data('edit_ietf_routing.json')
        cls.EDIT_PLUS_COMMIT_REQUEST = {
            "gentype": "basic",
            'prefix_namespaces': 'always',
            "commit": "add",
            "cfgd": cls.EDIT_CONFIG_CFGD,
        }
        cls.EDIT_PLUS_COMMIT_RAW = {
            "gentype": "raw",
            'prefix_namespaces': 'always',
            "commit": "add",
            "cfgd": cls.EDIT_CONFIG_CFGD,
        }

        cls.MULTI_RPC_REQUEST = canned_input_data('multi_rpc.basic.json')
        cls.GET_CONFIG_FILTER_XML = canned_output_str(
            'get_config_ocif.basic.filter.xml')
        cls.GET_CONFIG_FILTER_MINIMAL = canned_output_str(
            'get_config_ocif.basic.minimal.xml')
        cls.GET_CONFIG_XML_RAW = canned_output_str('get_config_ocif.raw.xml')

        cls.GET_CONFIG_WITH_DEFAULTS_CFGD = canned_input_data(
            'get_config_ocif_with_defaults.cfgd.json')

    def setUp(self):
        """Function called before each test case."""
        key = nconf.SessionKey('test', 'ios-xrv-6-2-1')
        if key in nconf.NetconfSession.instances:
            nconf.NetconfSession.instances[key].disconnect()
            del nconf.NetconfSession.instances[key]

    def test_gen_rpc_api_raw(self):
        """Test the gen_rpc_api() API and the gen_raw_rpc API.

        The gen_rpc_api API routes RPC generation to ncclient format (default).
        In this test, we set the gentype to raw which routes it to gen_raw_api.
        Takes dict/JSON as input and converts the XML Element tree returned by
        gen_raw_rpc() into a text string to be displayed to user.
        """
        # TODO, what's the minimal set of params?
        result = nconf.gen_rpc_api({'gentype': 'raw',
                                    'prefix_namespaces': 'always',
                                    'cfgd': self.GET_CONFIG_CFGD})
        # self.assertEqual(['ncrpcs', 'rpc'], sorted(result.keys()))
        self.assertEqual(self.GET_CONFIG_XML_RAW, result['rpc'])

        result = nconf.gen_rpc_api({
            "gentype": "raw",
            "prefix_namespaces": "minimal",
            "cfgd": {
                "proto-op": "rpc",
                "modules": {
                    "ietf-netconf": {
                        "namespace_prefixes": {
                            "nc": "urn:ietf:params:xml:ns:netconf:base:1.0",
                        },
                        "configs": [
                            {"xpath": "/nc:kill-session"}
                        ]}}}})
        self.assertEqual(u"""\
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <kill-session/>
</rpc>
""", result['rpc'])

        result = nconf.gen_rpc_api({
            "gentype": "raw",
            "cfgd": self.GET_CONFIG_WITH_DEFAULTS_CFGD,
        })

        self.assertEqual(
            canned_output_str("get_config_ocif_with_defaults.raw.xml"),
            result['rpc'])

        result = nconf.gen_rpc_api({
            "gentype": "raw",
            "prefix_namespaces": "always",
            "cfgd": self.GET_CONFIG_WITH_DEFAULTS_CFGD,
        })

        self.assertEqual(canned_output_str(
            "get_config_ocif_with_defaults.prefixes.raw.xml"),
            result['rpc'])

    def test_gen_rpc_value_prefixed(self):
        """Minimal prefix setting means no prefix in values for some RPCs."""
        result = nconf.gen_rpc_api({'gentype': 'raw',
                                    'prefix_namespaces': 'minimal',
                                    'segment': 1,
                                    'cfgd': self.EDIT_VALUE_PREFIXED})

        self.assertEqual(u"""\
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <edit-config>
    <target>
      <running/>
    </target>
    <config>
      <routing xmlns="urn:ietf:params:xml:ns:yang:ietf-routing">
        <routing-instance>
          <name>default</name>
          <routing-protocols>
            <routing-protocol>
              <type>static</type>
              <name>1</name>
              <static-routes>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ipv4-unicast-rou\
ting">
                  <route>
                    <destination-prefix>10.20.30.0/24</destination-prefix>
                    <next-hop>
                      <next-hop-address>192.168.10.1</next-hop-address>
                    </next-hop>
                  </route>
                </ipv4>
              </static-routes>
            </routing-protocol>
          </routing-protocols>
        </routing-instance>
      </routing>
    </config>
  </edit-config>
</rpc>
""", result['rpc'])

    def test_gen_rpc_api_basic(self):
        """Test the gen_rpc_api() API and the gen_ncclient_rpc API.

        The gen_rpc_api API routes RPC generation to ncclient format (default).
        Takes dict/JSON as input and converts the XML Element tree returned by
        gen_ncclient_rpc() into a text string to be displayed to user.
        """
        result = nconf.gen_rpc_api(self.GET_CONFIG_BASIC)
        self.assertEqual(['ncrpcs', 'rpc'], sorted(result.keys()))
        self.assertEqual(self.GET_CONFIG_FILTER_XML, result['rpc'])
        # result['ncrpcs'] = [(nc_op, kwargs), (nc_op, kwargs), ...]
        self.assertEqual(['get-config'],
                         [nc_op for nc_op, kwargs in result['ncrpcs']])
        self.assertEqual(
            [['filter', 'source']],
            [sorted(kwargs.keys()) for nc_op, kwargs in result['ncrpcs']])

    def test_gen_rpc_api_basic_minimal(self):
        """Test the gen_rpc_api() API and the gen_ncclient_rpc API.

        The gen_rpc_api API routes RPC generation to ncclient format (default).
        Takes dict/JSON as input and converts the XML Element tree returned by
        gen_ncclient_rpc() into a text string to be displayed to user.
        Specifies minimal prefix usage format.
        """
        result = nconf.gen_rpc_api(self.GET_CONFIG_BASIC_MINIMAL)
        self.assertEqual(['ncrpcs', 'rpc'], sorted(result.keys()))
        self.assertEqual(self.GET_CONFIG_FILTER_MINIMAL, result['rpc'])
        # result['ncrpcs'] = [(nc_op, kwargs), (nc_op, kwargs), ...]
        self.assertEqual(['get-config'],
                         [nc_op for nc_op, kwargs in result['ncrpcs']])
        self.assertEqual(
            [['filter', 'source']],
            [sorted(kwargs.keys()) for nc_op, kwargs in result['ncrpcs']])

    def test_gen_rpc_api_default_minimal(self):
        """Test the gen_rpc_api() API and the gen_ncclient_rpc API.

        The gen_rpc_api API routes RPC generation to ncclient format (default).
        Takes dict/JSON as input and converts the XML Element tree returned by
        gen_ncclient_rpc() into a text string to be displayed to user.
        Confirms that minimal prefix usage format is the default.
        """
        result = nconf.gen_rpc_api(self.GET_CONFIG_MINIMAL_DEFAULT)
        self.assertEqual(['ncrpcs', 'rpc'], sorted(result.keys()))
        self.assertEqual(self.GET_CONFIG_FILTER_MINIMAL, result['rpc'])
        # result['ncrpcs'] = [(nc_op, kwargs), (nc_op, kwargs), ...]
        self.assertEqual(['get-config'],
                         [nc_op for nc_op, kwargs in result['ncrpcs']])
        self.assertEqual(
            [['filter', 'source']],
            [sorted(kwargs.keys()) for nc_op, kwargs in result['ncrpcs']])

    SCRIPT_HEAD = """\
#! /usr/bin/env python
import traceback
import lxml.etree as et
from argparse import ArgumentParser
from ncclient import manager
from ncclient.operations import RPCError

payload = [
'''
"""

    SCRIPT_FOOT = """
''',
]

if __name__ == '__main__':

    parser = ArgumentParser(description='Usage:')

    # script arguments
    parser.add_argument('-a', '--host', type=str, required=True,
                        help="Device IP address or Hostname")
    parser.add_argument('-u', '--username', type=str, required=True,
                        help="Device Username (netconf agent username)")
    parser.add_argument('-p', '--password', type=str, required=True,
                        help="Device Password (netconf agent password)")
    parser.add_argument('--port', type=int, default=830,
                        help="Netconf agent port")
    args = parser.parse_args()

    # connect to netconf agent
    with manager.connect(host=args.host,
                         port=args.port,
                         username=args.username,
                         password=args.password,
                         timeout=90,
                         hostkey_verify=False,
                         device_params={'name': 'csr'}) as m:

        # execute netconf operation
        for rpc in payload:
            try:
                response = m.dispatch(et.fromstring(rpc))
                data = response.xml
            except RPCError as e:
                data = e.xml
                pass
            except Exception as e:
                traceback.print_exc()
                exit(1)

            # beautify output
            if et.iselement(data):
                data = et.tostring(data, pretty_print=True).decode()

            try:
                out = et.tostring(
                    et.fromstring(data.encode('utf-8')),
                    pretty_print=True
                ).decode()
            except Exception as e:
                traceback.print_exc()
                exit(1)

            print(out)
"""

    def test_gen_rpc_api_script(self):
        """Generation of Python script for an RPC."""
        result = nconf.gen_rpc_api(self.GET_CONFIG_SCRIPT)
        self.assertEqual(self.SCRIPT_HEAD + """\
<nc:get-config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <nc:source>
    <nc:running/>
  </nc:source>
  <nc:filter>
    <ocif:interfaces xmlns:ocif="http://openconfig.net/yang/interfaces">
      <ocif:interface>
        <ocif:name>GigabitEthernet1</ocif:name>
      </ocif:interface>
    </ocif:interfaces>
  </nc:filter>
</nc:get-config>""" + self.SCRIPT_FOOT, result['rpc'])

    def test_gen_rpc_api_negative(self):
        """Input validation and other failure cases."""
        # No cfgd
        self.assertEqual({'rpc': 'Failed to generate RPC', 'ncrpcs': []},
                         nconf.gen_rpc_api({}))
        # Missing gentype
        self.assertEqual({'rpc': 'Failed to generate RPC', 'ncrpcs': []},
                         nconf.gen_rpc_api(
                             {'cfgd': {'dsstore': 'candidate',
                                       'proto-op': 'edit-config',
                                       'modules': {}}}))
        # Invalid args in cfgd
        data = copy.deepcopy(self.GET_CONFIG_MINIMAL_DEFAULT)
        data['cfgd']['modules']['openconfig-interfaces']['configs'][0]['xpath'] = 'foo/'    # noqa: E501
        self.assertEqual({
            'rpc': """\
ERROR: Invalid xpath:
foo/
  must start with '/'""",
            'ncrpcs': [],
        }, nconf.gen_rpc_api(data))

        data['gentype'] = 'raw'
        self.assertEqual({
            'rpc': """\
ERROR: Invalid xpath:
foo/
  must start with '/'""",
            'ncrpcs': [],
        }, nconf.gen_rpc_api(data))

        data['gentype'] = 'script'
        # Script needs a list of cfgd dicts
        data['cfgd'] = [{'cfgd': data['cfgd']}]
        self.assertEqual({
            'rpc': """\
ERROR: Invalid xpath:
foo/
  must start with '/'""",
            'ncrpcs': [],
        }, nconf.gen_rpc_api(data))

    def test_gen_rpc_api_absolute_minimum_raw(self):
        """Construction of minimal valid RPCs in 'raw' format."""
        self.assertEqual({'ncrpcs': [], 'rpc': u"""\
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <get-config>
    <source>
      <running/>
    </source>
  </get-config>
</rpc>
"""},
                         nconf.gen_rpc_api({
                             'gentype': 'raw',
                             'cfgd': {
                                 'proto-op': 'get-config',
                                 'dsstore': 'running',
                             }}))

        self.assertEqual({'ncrpcs': [], 'rpc': u"""\
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <edit-config>
    <target>
      <running/>
    </target>
    <config/>
  </edit-config>
</rpc>
"""},
                         nconf.gen_rpc_api({
                             'gentype': 'raw',
                             'commit': 'add',   # IGNORED, running != candidate
                             'cfgd': {
                                 'proto-op': 'edit-config',
                                 'dsstore': 'running',
                             }}))

        self.assertEqual({'ncrpcs': [], 'rpc': u"""\
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <get/>
</rpc>
"""},
                         nconf.gen_rpc_api({
                             'gentype': 'raw',
                             'cfgd': {
                                 'proto-op': 'get',
                                 'modules': {},
                             }}))

    def test_gen_rpc_api_absolute_minimum_basic(self):
        """Construction of minimal valid RPCs in 'basic' format."""
        self.assertEqual({'ncrpcs': [['get-config', {'source': 'running'}]],
                          'rpc': ""},
                         nconf.gen_rpc_api({
                             'gentype': 'basic',
                             'cfgd': {
                                 'proto-op': 'get-config',
                                 'dsstore': 'running',
                             }}))

        self.assertEqual({'ncrpcs': [['edit-config', {'target': 'running'}]],
                          'rpc': ""},
                         nconf.gen_rpc_api({
                             'gentype': 'basic',
                             'commit': 'add',   # IGNORED, running != candidate
                             'cfgd': {
                                 'proto-op': 'edit-config',
                                 'dsstore': 'running',
                             }}))

        self.assertEqual({'ncrpcs': [['get', {}]],
                          'rpc': ""},
                         nconf.gen_rpc_api({
                             'gentype': 'basic',
                             'cfgd': {
                                 'proto-op': 'get',
                                 'modules': {},
                             }}))

    def test_gen_rpc_api_get(self):
        """Construction of a GET request."""
        result = nconf.gen_rpc_api(self.GET_RUN)
        nc_op, kwargs = result['ncrpcs'][0]
        self.assertEqual("get", nc_op)
        # 'basic' XML should NOT have an assigned netconf namespace,
        # just namespaces for the module(s) being handled
        self.assertEqual("""\
<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <ocif:interfaces xmlns:ocif="http://openconfig.net/yang/interfaces">
    <ocif:interface>
      <ocif:name>MgmtEth0/RP0/CPU0/0</ocif:name>
    </ocif:interface>
  </ocif:interfaces>
</nc:filter>
""", et.tostring(kwargs['filter'],
                 encoding='unicode',
                 pretty_print=True))

        self.assertEqual("report-all-tagged", kwargs['with_defaults'])

    EDIT_REQUEST_XML_BASIC = """\
<nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <ocif:interfaces xmlns:ocif="http://openconfig.net/yang/interfaces">
    <ocif:interface nc:operation="replace">
      <ocif:name>GigabitEthernet0/0/0/0</ocif:name>
      <ocif:config>
        <ocif:enabled>true</ocif:enabled>
      </ocif:config>
    </ocif:interface>
  </ocif:interfaces>
</nc:config>
"""
    COMMIT_REQUEST_XML_BASIC = """<commit/>\n"""

    EDIT_REQUEST_XML_RAW = """\
<nc:rpc xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:message-id="101">
  <nc:edit-config>
    <nc:target>
      <nc:candidate/>
    </nc:target>
    <nc:config>
      <ocif:interfaces xmlns:ocif="http://openconfig.net/yang/interfaces">
        <ocif:interface nc:operation="replace">
          <ocif:name>GigabitEthernet0/0/0/0</ocif:name>
          <ocif:config>
            <ocif:enabled>true</ocif:enabled>
          </ocif:config>
        </ocif:interface>
      </ocif:interfaces>
    </nc:config>
  </nc:edit-config>
</nc:rpc>
"""

    COMMIT_REQUEST_XML_RAW = """\
<nc:rpc xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:message-id="102">
  <nc:commit/>
</nc:rpc>
"""

    def test_gen_rpc_api_commit_basic(self):
        """Make sure a basic RPC with commit is correctly generated."""
        result = nconf.gen_rpc_api(self.EDIT_PLUS_COMMIT_REQUEST)
        self.assertEqual(['ncrpcs', 'rpc'], sorted(result.keys()))
        self.assertEqual((self.EDIT_REQUEST_XML_BASIC + "\n" +
                          self.COMMIT_REQUEST_XML_BASIC),
                         result['rpc'])
        # result['ncrpcs'] = [(nc_op, kwargs), (nc_op, kwargs), ...]
        self.assertEqual(['edit-config', 'commit'],
                         [nc_op for nc_op, kwargs in result['ncrpcs']])
        self.assertEqual(
            [['config', 'target'], []],
            [sorted(kwargs.keys()) for nc_op, kwargs in result['ncrpcs']])

    def test_gen_rpc_api_commit_raw(self):
        """Make sure a raw RPC with commit is correctly generated."""
        result = nconf.gen_rpc_api(self.EDIT_PLUS_COMMIT_RAW)
        self.assertEqual(['ncrpcs', 'rpc'], sorted(result.keys()))
        self.assertEqual((self.EDIT_REQUEST_XML_RAW + "\n" +
                          self.COMMIT_REQUEST_XML_RAW),
                         result['rpc'])
        self.assertEqual([], result['ncrpcs'])

    def test_gen_rpc_api_commit_script(self):
        """Make sure a script RPC with commit is correctly generated."""
        result = nconf.gen_rpc_api({'gentype': 'script',
                                    'prefix_namespaces': 'always',
                                    'cfg': json.dumps([{
                                        'commit': 'add',
                                        'cfgd': self.EDIT_CONFIG_CFGD}])})
        self.assertEqual(self.SCRIPT_HEAD + """\
<nc:edit-config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <nc:target>
    <nc:candidate/>
  </nc:target>
  <nc:config>
    <ocif:interfaces xmlns:ocif="http://openconfig.net/yang/interfaces">
      <ocif:interface nc:operation="replace">
        <ocif:name>GigabitEthernet0/0/0/0</ocif:name>
        <ocif:config>
          <ocif:enabled>true</ocif:enabled>
        </ocif:config>
      </ocif:interface>
    </ocif:interfaces>
  </nc:config>
</nc:edit-config>
''','''
<nc:commit xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"/>""" +
                         self.SCRIPT_FOOT, result['rpc'])

    def test_commit_rpc_negative(self):
        """Input validation check."""
        self.assertRaises(ValueError, nconf._commit_rpc, 'unknown')

    def test_gen_rpc_api_multirpc(self):
        """Construction of multiple custom RPC requests."""
        result = nconf.gen_rpc_api(self.MULTI_RPC_REQUEST)
        self.assertEqual(['ncrpcs', 'rpc'], sorted(result.keys()))
        self.assertEqual("""\
<nc:lock xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <nc:target>
    <nc:candidate/>
  </nc:target>
</nc:lock>
<nc:unlock xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <nc:target>
    <nc:candidate/>
  </nc:target>
</nc:unlock>\n""", result['rpc'])
        # result['ncrpcs'] = [(nc_op, kwargs), (nc_op, kwargs), ...]
        self.assertEqual(['rpc', 'rpc'],
                         [nc_op for nc_op, kwargs in result['ncrpcs']])
        self.assertEqual(
            [['rpc_command'], ['rpc_command']],
            [sorted(kwargs.keys()) for nc_op, kwargs in result['ncrpcs']])

    def test_gen_task_api_basic(self):
        """Load a task and construct a 'basic' style RPC from it."""
        th = tasks.TaskHandler('getMgmt', get_path('tasks_dir', user='test'),
                               {'category': 'default'})
        replay = th.retrieve_task()
        ret = nconf.gen_task_api(replay,
                                 {'dsstore': 'candidate',
                                  'prefixes': 'always',
                                  'gentype': 'basic'})
        self.assertEqual(canned_output_data('getMgmt.basic.json'), ret)

    def test_gen_task_api_minimal(self):
        """Load a task and construct a 'basic' RPC with minimal prefixes."""
        th = tasks.TaskHandler('getMgmt', get_path('tasks_dir', user='test'),
                               {'category': 'default'})
        replay = th.retrieve_task()
        ret = nconf.gen_task_api(replay,
                                 {'dsstore': 'candidate',
                                  'prefixes': 'minimal',
                                  'gentype': 'basic'})
        self.assertEqual(canned_output_data('getMgmt.minimal.json'), ret)

    def test_gen_task_api_run(self):
        """Load a task and construct a 'run' style RPC from it."""
        th = tasks.TaskHandler('getMgmt', get_path('tasks_dir', user='test'),
                               {'category': 'default'})
        replay = th.retrieve_task()
        ret = nconf.gen_task_api(replay,
                                 {'dsstore': 'candidate',
                                  'prefixes': 'always',
                                  'gentype': 'run'})
        # Type 'run' returns lxml Element instances but it's easier to
        # compare against a string
        self.assertTrue(et.iselement(ret['ncrpcs'][0][1]['filter']))
        ret['ncrpcs'][0][1]['filter'] = et.tostring(
            ret['ncrpcs'][0][1]['filter'], encoding="unicode",
            pretty_print=True)
        self.assertEqual(canned_output_data('getMgmt.run.json'), ret)

    def test_gen_task_api_script(self):
        """Construct a 'script' style RPC from a task."""
        th = tasks.TaskHandler('getMgmt', get_path('tasks_dir', user='test'),
                               {'category': 'default'})
        replay = th.retrieve_task()
        ret = nconf.gen_task_api(replay,
                                 {'dsstore': 'running',
                                  'prefixes': 'always',
                                  'gentype': 'script'})
        self.assertEqual({
            'info': [['openconfig-interfaces', '2016-12-22']],
            'error': '',
            'ncrpcs': [canned_output_str('getMgmt.raw.xml')],
            'segments': Template(nconf.script_template).render(
                {'rpcs': [canned_output_str('getMgmt.raw.xml')]}),
        }, ret)

    def test_gen_task_api_edit_commit(self):
        """Confirm that gen_task_api() works for edit-config + commit too."""
        th = tasks.TaskHandler('config-mgmt',
                               get_path('tasks_dir', user='test'),
                               {'category': 'default'})
        replay = th.retrieve_task()
        ret = nconf.gen_task_api(replay,
                                 {'dsstore': 'candidate',
                                  'prefixes': 'always',
                                  'gentype': 'run'})
        # Type 'run' returns lxml Element instances but it's easier to
        # compare against a string
        self.assertTrue(et.iselement(ret['ncrpcs'][0][1]['config']))
        cfgmgmt = canned_output_data('config-mgmt.run.json')
        foobar = et.fromstring(cfgmgmt['ncrpcs'][0][1]['config'])

        for fp in zip(foobar.iter(), ret['ncrpcs'][0][1]['config'].iter()):
            self.assertEqual(fp[0].tag, fp[1].tag)
            self.assertEqual(fp[0].nsmap, fp[1].nsmap)

    def test_gen_task_api_custom(self):
        """Verify gen_task_api() with custom RPCs."""
        th = tasks.TaskHandler('custom', get_path('tasks_dir', user='test'),
                               {'category': 'default'})
        replay = th.retrieve_task()
        ret = nconf.gen_task_api(replay,
                                 {'dsstore': 'candidate',
                                  'prefixes': 'always',
                                  'gentype': 'run'})
        # Type 'run' returns lxml Element instances but it's easier to
        # compare against a string
        self.assertTrue(et.iselement(ret['ncrpcs'][0][1]['rpc_command']))
        ret['ncrpcs'][0][1]['rpc_command'] = et.tostring(
            ret['ncrpcs'][0][1]['rpc_command'], encoding="unicode",
            pretty_print=True)
        self.assertTrue(et.iselement(ret['ncrpcs'][1][1]['rpc_command']))
        ret['ncrpcs'][1][1]['rpc_command'] = et.tostring(
            ret['ncrpcs'][1][1]['rpc_command'], encoding="unicode",
            pretty_print=True)

        self.assertEqual(canned_output_data('custom.run.json'), ret)

    def test_ncclient_supported_platforms(self):
        """Spot check of the ncclient_supported_platforms API."""
        plats = nconf.ncclient_supported_platforms()
        self.assertIn('nexus', plats)
        self.assertIn('iosxr', plats)
        self.assertIn('iosxe', plats)

    @patch('ysnetconf.nconf.manager.connect')
    def test_ncclient_send_nothing(self, m_connect):
        """Sanity check of ncclient_send with no actual RPCs."""
        key = nconf.SessionKey('test', 'ios-xrv-6-2-1')
        mock_manager(m_connect)

        nconf.ncclient_send(key, [])

        m_connect.assert_called_once()
        nc_log = nconf.NetconfSession.get(key).message_log

        self.assertEqual(nc_log.popleft(),
                         'No session found. Creating a new temporary session')
        self.assertEqual(nc_log.popleft(),
                         'NETCONF CONNECTED 127.0.0.1:2224')
        self.assertEqual(nc_log.popleft(),
                         'NETCONF DISCONNECT 127.0.0.1:2224')
        self.assertEqual(0, len(nc_log))

    @patch('ysnetconf.nconf.manager.connect')
    def test_ncclient_send_all_rpcs(self, m_connect):
        """Exercise ncclient_send with various RPCs."""
        key = nconf.SessionKey('test', 'ios-xrv-6-2-1')
        # Mock out the Manager class and the behavior of its various APIs.
        m_manager = mock_manager(m_connect)
        m_manager.edit_config.return_value = MagicMock(
            spec=ncclient.operations.RPCReply)
        m_manager.edit_config.return_value.xml = '<rpc-reply><ok/></rpc-reply>'
        m_manager.commit.return_value = MagicMock(
            spec=ncclient.operations.RPCReply)
        m_manager.commit.return_value.xml = '<rpc-reply><ok/></rpc-reply>'
        m_manager.get_config.return_value = MagicMock(
            spec=ncclient.operations.GetReply)
        m_manager.get_config.return_value.xml = \
            "<rpc-reply><data/></rpc-reply>"
        nconf_session = nconf.NetconfSession.get(key)

        # edit-config + commit
        ncrpcs = nconf.gen_rpc_api(self.EDIT_PLUS_COMMIT_REQUEST)['ncrpcs']
        # get-config
        ncrpcs += nconf.gen_rpc_api(self.GET_CONFIG_BASIC)['ncrpcs']
        # TODO: get, rpc
        ret = nconf.ncclient_send(key, ncrpcs)

        nc_log = nconf_session.message_log

        m_connect.assert_called_once()
        self.assertEqual(nc_log.popleft(),
                         'No session found. Creating a new temporary session')
        self.assertEqual(nc_log.popleft(),
                         'NETCONF CONNECTED 127.0.0.1:2224')

        # edit-config
        self.assertEqual(nc_log.popleft(),
                         "NETCONF SEND edit-config")
        self.assertEqual(
            nc_log.popleft(),
            '<?xml version="1.0" ?>\n<rpc-reply>\n  <ok/>\n</rpc-reply>\n'
        )

        m_manager.edit_config.assert_called_once()
        args, kwargs = m_manager.edit_config.call_args
        self.assertEqual(kwargs['target'], "candidate")
        self.assertTrue(et.iselement(kwargs['config']))
        self.assertEqual(nc_log.popleft(),
                         "NETCONF edit-config COMPLETE")

        # commit
        self.assertEqual(nc_log.popleft(),
                         "NETCONF SEND commit")
        m_manager.commit.assert_called_once()
        self.assertEqual(
            nc_log.popleft(),
            '<?xml version="1.0" ?>\n<rpc-reply>\n  <ok/>\n</rpc-reply>\n'
        )
        self.assertEqual(nc_log.popleft(),
                         "NETCONF commit COMPLETE")

        # get-config
        self.assertEqual(nc_log.popleft(),
                         "NETCONF SEND get-config")
        self.assertEqual(
            nc_log.popleft(),
            '<?xml version="1.0" ?>\n<rpc-reply>\n  <data/>\n</rpc-reply>\n'
        )
        m_manager.get_config.assert_called_once()
        args, kwargs = m_manager.get_config.call_args
        self.assertEqual(kwargs['source'], "running")
        self.assertTrue(et.iselement(kwargs['filter']))
        self.assertEqual(nc_log.popleft(),
                         "NETCONF get-config COMPLETE")

        self.assertEqual(ret, [
            ('edit-config',
             '<?xml version="1.0" ?>\n<rpc-reply>\n  <ok/>\n</rpc-reply>\n'),
            ('commit',
             '<?xml version="1.0" ?>\n<rpc-reply>\n  <ok/>\n</rpc-reply>\n'),
            ('get-config',
             '<?xml version="1.0" ?>\n<rpc-reply>\n  <data/>\n</rpc-reply>\n'),
        ])

    @patch('ysnetconf.nconf.manager.connect')
    def test_ncclient_send_negative(self, m_connect):
        """Test various failure scenarios of ncclient_send."""
        # Exception is raised if device doesn't support netconf
        self.assertRaises(nconf.NetconfNotSupported,
                          nconf.ncclient_send,
                          nconf.SessionKey('test', 'ios-xrv'),
                          [])

        # device_params sets to 'default' if platform unknown
        key = nconf.SessionKey('test', 'ios-xrv-6-2-1')
        devprofile = nconf.NetconfSession.get(key).dev_profile
        devprofile.netconf.device_variant = "elevated or shoes"
        nconf.ncclient_send(key, [])
        m_connect.assert_called_once_with(
            host=devprofile.netconf.address,
            port=devprofile.netconf.port,
            username=devprofile.netconf.username,
            password=devprofile.netconf.password,
            device_params={'name': 'default'},
            timeout=30)

        # exceptions are handled
        m_manager = mock_manager(m_connect)
        m_manager.get.side_effect = NCClientError
        m_manager.dispatch.side_effect = RuntimeError("Raised as expected")

        nconf.ncclient_send(
            key,
            [('get', {'filter': et.Element("filter")}),
             ('rpc', {'rpc_command': et.Element("dunno")})],
        )
        m_manager.get.assert_called_once()
        m_manager.dispatch.assert_called_once()

    @patch('ysnetconf.nconf.manager.connect')
    def test_ncclient_server_capabilities_report(self, m_connect):
        """Test ncclient_server_capabilities_report API."""
        m_manager = mock_manager(m_connect)
        key = nconf.SessionKey('test', 'ios-xrv-6-2-1')
        p = PropertyMock(return_value=[
            nconf.CAP_CANDIDATE,
            nconf.CAP_WRITABLE_RUN,
            nconf.CAP_STARTUP,
            ('urn:ietf:params:netconf:capability:with-defaults:1.0?'
             'basic-mode=explicit&also-supported=report-all-tagged'),
            'urn:not:a:netconf:capability',
            ('http://openconfig.net/yang/network-instance?'
             'module=openconfig-network-instance&revision=2017-01-13'
             '&deviations=cisco-xe-openconfig-bgp-deviation,'
             'cisco-xe-openconfig-network-instance-deviation'),
        ])
        type(m_manager).server_capabilities = p

        # Note that:
        # 1) NETCONF capabilities are first in the list,
        #    even if other capabilities are first alphabetically
        # 2) Within a category of capabilities, they're alphabetical
        self.assertEqual([
            # NETCONF capabilities are first, in alphabetical order
            {'capability': nconf.CAP_CANDIDATE},
            {'capability': nconf.CAP_STARTUP},
            {
                'capability':
                'urn:ietf:params:netconf:capability:with-defaults:1.0',
                'also-supported': 'report-all-tagged',
                'basic-mode': 'explicit',
            },
            {'capability': nconf.CAP_WRITABLE_RUN},
            # OpenConfig YANG module capabilities come before...
            {
                'capability': 'http://openconfig.net/yang/network-instance',
                'module': 'openconfig-network-instance',
                'revision': '2017-01-13',
                'deviations': [
                    'cisco-xe-openconfig-bgp-deviation',
                    'cisco-xe-openconfig-network-instance-deviation',
                ],
            },
            # ...miscellaneous capabilities
            {'capability': 'urn:not:a:netconf:capability'},
        ], nconf.ncclient_server_capabilities_report(key))

    @patch('ysnetconf.nconf.manager.connect')
    def test_ncclient_server_datastores(self, m_connect):
        """Test ncclient_server_datastores API."""
        m_manager = mock_manager(m_connect)

        # Exception is raised if device doesn't support netconf
        key = nconf.SessionKey('test', 'ios-xrv-6-2-1')

        # No capabilities
        p = PropertyMock(return_value=[])
        type(m_manager).server_capabilities = p

        self.assertEqual(['running'],
                         nconf.ncclient_server_datastores(key, 'get-config'))
        self.assertEqual([],
                         nconf.ncclient_server_datastores(key, 'edit-config'))
        self.assertEqual(['running'],
                         nconf.ncclient_server_datastores(key, 'rpc'))

        # All currently relevant capabilities
        p = PropertyMock(return_value=[
            nconf.CAP_CANDIDATE,
            nconf.CAP_WRITABLE_RUN,
            nconf.CAP_STARTUP,
        ])
        type(m_manager).server_capabilities = p

        self.assertEqual(['candidate', 'running', 'startup'],
                         nconf.ncclient_server_datastores(key, 'get-config'))
        self.assertEqual(['candidate', 'running'],
                         nconf.ncclient_server_datastores(key, 'edit-config'))
        self.assertEqual(['candidate', 'running', 'startup'],
                         nconf.ncclient_server_datastores(key, 'rpc'))
