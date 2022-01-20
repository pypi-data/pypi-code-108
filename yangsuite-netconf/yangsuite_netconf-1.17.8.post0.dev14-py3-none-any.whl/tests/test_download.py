# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
# -*- coding: utf-8 -*-
"""Tests ysnetconf/views/download.py"""
import os.path
import os
import tempfile
import shutil
import lxml.etree as et
import ncclient.operations

try:
    # Django 2.x
    from django.urls import reverse
except ImportError:
    # Django 1.x
    from django.core.urlresolvers import reverse

from django_webtest import WebTest
from yangsuite.paths import set_base_path
from mock import patch, MagicMock, PropertyMock
from ncclient.transport.errors import SSHError
from ysfilemanager import merge_user_set
from .utilities import mock_manager


def clone_test_data(new_location):
    if os.path.exists(new_location):
        shutil.rmtree(new_location)
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'data'),
                    new_location)
    set_base_path(new_location)


class TestListSchemas(WebTest):
    """Tests list_schemas function"""
    csrf_checks = False
    testdir = os.path.join(os.path.dirname(__file__), 'data')

    def setUp(self):
        """Function that will be called before the start of each test"""
        self.url_list = reverse('netconf:listschemas')
        set_base_path(self.testdir)
        self.temp_path = tempfile.mkdtemp()

    def test_access_restriction(self):
        """No user --> login page; logged in --> results.html"""
        resp = self.app.get(self.url_list)
        self.assertRedirects(resp, "/accounts/login/?next=" + self.url_list)

    def test_no_device(self):
        """No Device specified -> JSON Response with error"""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_list,
                             user='user',
                             expect_errors=True)
        data = resp.json
        self.assertEqual(resp.status, "400 No device specified")
        self.assertEqual({}, data)

    def test_no_device_profile(self):
        """Device profile does not exist -> JSON Response with error"""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_list,
                             user='user',
                             params=dict(device="IOS"),
                             expect_errors=True)
        data = resp.json
        self.assertEqual(resp.status, '404 Device profile "IOS" not found')
        self.assertEqual({}, data)

    def test_device_no_netconf(self):
        """Device doesn't support NETCONF -> JSON Response with error"""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_list,
                             user="user",
                             params=dict(device="ios-xrv"),
                             expect_errors=True)
        self.assertEqual(
            resp.status,
            '400 Device "IOS XRv" is not marked as supporting NETCONF')
        data = resp.json
        self.assertEqual({
            'reply': 'Device "IOS XRv" is not marked as supporting NETCONF',
        }, data)

    @patch('ysnetconf.nconf.manager.connect')
    def test_SSHError(self, m_connect):
        """Raise SSHError while connecting"""
        clone_test_data(self.temp_path)
        mock_manager(m_connect)
        m_connect.side_effect = SSHError
        resp = self.app.post(self.url_list,
                             user="user",
                             params=dict(device="ios-xrv-6-2-1"),
                             expect_errors=True)

        self.assertEqual(
                    resp.status,
                    '502 SSH connection refused by device "IOS XRv 6.2.1"')
        data = resp.json
        self.assertEqual({}, data)

    @patch('ysnetconf.nconf.manager.connect')
    def test_generic_exception(self, m_connect):
        """Raise Exception while connecting"""
        clone_test_data(self.temp_path)
        mock_manager(m_connect)
        m_connect.side_effect = Exception("It's a trap!")
        resp = self.app.post(self.url_list,
                             user="user",
                             params=dict(device="ios-xrv-6-2-1"),
                             expect_errors=True)

        self.assertEqual(
                    resp.status,
                    "500 Exception: It's a trap!")
        data = resp.json
        self.assertEqual({}, data)

    @patch('ysnetconf.nconf.manager.connect')
    def test_get_schema_list_via_capabilities_success(self, m_connect):
        """Without netconf-monitoring, get list of schemas via capabilities."""
        clone_test_data(self.temp_path)
        m_manager = mock_manager(m_connect)
        # Note that ietf-netconf-monitoring is NOT in this list
        caps = [
            "urn:ietf:params:netconf:capability:rollback-on-error:1.0",
            "urn:ietf:params:xml:ns:yang:ietf-yang-types?"
            "module=ietf-yang-types&revision=2013-07-15",
            "urn:ietf:params:netconf:capability:validate:1.1",
            "urn:ietf:params:xml:ns:yang:ietf-inet-types?"
            "module=ietf-inet-types&revision=2013-07-15",
            "urn:ietf:params:netconf:base:1.1",
            "urn:ietf:params:netconf:capability:confirmed-commit:1.1",
            "urn:ietf:params:netconf:capability:candidate:1.0",
            "urn:ietf:params:xml:ns:yang:ietf-syslog-types?"
            "module=ietf-syslog-types&revision=2015-11-09"
        ]
        exp_resp = {
            "schemas": [
                    {"name": "ietf-inet-types", "revision": "2013-07-15"},
                    {"name": "ietf-syslog-types", "revision": "2015-11-09"},
                    {"name": "ietf-yang-types", "revision": "2013-07-15"}
            ]
        }
        p = PropertyMock(return_value=caps)
        type(m_manager).server_capabilities = p
        resp = self.app.post(self.url_list,
                             user="user",
                             params=dict(device="ios-xrv-6-2-1"),
                             expect_errors=False)
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertIn('reply', data)
        self.assertEqual(exp_resp, data['reply'])

    @patch('ysnetconf.nconf.manager.connect')
    def test_get_schema_list_via_netconf_monitoring_success(self, m_connect):
        """Get list of schemas via ietf-netconf-monitoring capability."""
        clone_test_data(self.temp_path)
        m_manager = mock_manager(m_connect)
        caps = [
            "urn:ietf:params:netconf:base:1.0",
            "urn:ietf:params:netconf:base:1.1",
            "urn:ietf:params:netconf:capability:writable-running:1.0",
            "urn:ietf:params:netconf:capability:xpath:1.0",
            "urn:ietf:params:netconf:capability:validate:1.0",
            "urn:ietf:params:netconf:capability:validate:1.1",
            # ...
            "urn:ietf:params:xml:ns:yang:ietf-key-chain?module=ietf-key-chain"
            "&amp;revision=2015-02-24"
            "&amp;features=independent-send-accept-lifetime,hex-key-string,"
            "accept-tolerance",
            # Why yes, we DO support ietf-netconf-monitoring!
            "urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring"
            "?module=ietf-netconf-monitoring&amp;revision=2010-10-04",
            "urn:ietf:params:xml:ns:yang:ietf-netconf-notifications"
            "?module=ietf-netconf-notifications&amp;revision=2012-02-06",
            # ...
        ]
        p = PropertyMock(return_value=caps)
        type(m_manager).server_capabilities = p

        m_manager.get.return_value = MagicMock(
            spec=ncclient.operations.GetReply)
        m_manager.get.return_value.data_ele = et.fromstring("""
<data>
 <netconf-state xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring">
  <schemas>
   <schema>
    <identifier>Cisco-IOS-XE-interface-common</identifier>
    <version>2017-08-16</version>
    <format>yang</format>
    <namespace>http://cisco.com/ns/yang/Cisco-IOS-XE-interface-common\
</namespace>
    <location>NETCONF</location>
   </schema>
   <schema>
    <identifier>Cisco-IOS-XE-interfaces</identifier>
    <version>2017-08-30</version>
    <format>yang</format>
    <namespace>http://cisco.com/ns/yang/Cisco-IOS-XE-native</namespace>
    <location>NETCONF</location>
   </schema>
   <schema>
    <identifier>Cisco-IOS-XE-ip</identifier>
    <version>2017-08-28</version>
    <format>yang</format>
    <namespace>http://cisco.com/ns/yang/Cisco-IOS-XE-native</namespace>
    <location>NETCONF</location>
   </schema>
  </schemas>
 </netconf-state>
</data>""")

        exp_resp = {"schemas": [
            {"name": "Cisco-IOS-XE-interface-common",
             "revision": "2017-08-16"},
            {"name": "Cisco-IOS-XE-interfaces", "revision": "2017-08-30"},
            {"name": "Cisco-IOS-XE-ip", "revision": "2017-08-28"}
        ]}

        resp = self.app.post(self.url_list,
                             user="user",
                             params=dict(device="ios-xrv-6-2-1"),
                             expect_errors=False)
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertIn('reply', data)
        self.assertEqual(exp_resp, data['reply'])

    @patch('ysnetconf.nconf.manager.connect')
    def test_get_schema_list_via_yang_library_success(self, m_connect):
        """Get list of schemas via ietf-yang-library capability."""
        clone_test_data(self.temp_path)
        m_manager = mock_manager(m_connect)
        caps = [
            "urn:ietf:params:netconf:base:1.0",
            "urn:ietf:params:netconf:base:1.1",
            "urn:ietf:params:netconf:capability:writable-running:1.0",
            "urn:ietf:params:netconf:capability:xpath:1.0",
            "urn:ietf:params:netconf:capability:validate:1.0",
            "urn:ietf:params:netconf:capability:validate:1.1",
            # Why yes, we DO support ietf-yang-library!
            "urn:ietf:params:netconf:capability:yang-library:1.0",
            # ...
            "urn:ietf:params:xml:ns:yang:ietf-key-chain?module=ietf-key-chain"
            "&amp;revision=2015-02-24"
            "&amp;features=independent-send-accept-lifetime,hex-key-string,"
            "accept-tolerance",
            "urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring"
            "?module=ietf-netconf-monitoring&amp;revision=2010-10-04",
            "urn:ietf:params:xml:ns:yang:ietf-netconf-notifications"
            "?module=ietf-netconf-notifications&amp;revision=2012-02-06",
            # ...
        ]
        p = PropertyMock(return_value=caps)
        type(m_manager).server_capabilities = p

        m_manager.get.return_value = MagicMock(
            spec=ncclient.operations.GetReply)
        m_manager.get.return_value.data_ele = et.fromstring("""
<data>
 <modules-state xmlns="urn:ietf:params:xml:ns:yang:ietf-yang-library">
  <module>
   <name>Cisco-IOS-XE-native</name>
   <revision>2018-08-10</revision>
   <submodule>
     <name>Cisco-IOS-XE-interfaces</name>
     <revision>2018-09-28</revision>
   </submodule>
  </module>
 </modules-state>
</data>""")

        exp_resp = {"schemas": [
            # in alphabetical order by name
            {"name": "Cisco-IOS-XE-interfaces", "revision": "2018-09-28"},
            {"name": "Cisco-IOS-XE-native",
             "revision": "2018-08-10"},
        ]}

        resp = self.app.post(self.url_list,
                             user="user",
                             params=dict(device="ios-xrv-6-2-1"),
                             expect_errors=False)
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertIn('reply', data)
        self.assertEqual(exp_resp, data['reply'])

    def tearDown(self):
        """Burn it all to the ground"""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)


class TestDownloadSchemas(WebTest):
    """Tests download_schemas function"""
    csrf_checks = False
    testdir = os.path.join(os.path.dirname(__file__), 'data')
    nc_monitor = "urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring"
    schema_list = """
[
   [
      "Cisco-IOS-XR-Ethernet-SPAN-cfg",
      "2015-11-09"
   ],
   [
      "Cisco-IOS-XR-Ethernet-SPAN-datatypes",
      "2015-11-09"
   ],
   [
      "Cisco-IOS-XR-Ethernet-SPAN-oper",
      "2015-11-09"
   ],
   [
      "Cisco-IOS-XR-aaa-aaacore-cfg",
      "2015-11-09"
   ]
]
"""

    schema_list_mgmt_test = """
[
   [
      "cisco-self-mgmt-test",
      "2016-06-15"
   ]
]
"""

    def setUp(self):
        """Function that will be called before the start of each test"""
        self.url_download = reverse('netconf:downloadschemas')
        set_base_path(self.testdir)
        self.temp_path = tempfile.mkdtemp()

    def test_access_restriction(self):
        """No user --> login page; logged in --> results.html"""
        resp = self.app.get(self.url_download)
        self.assertRedirects(resp,
                             "/accounts/login/?next=" + self.url_download)

    def test_no_repo(self):
        """No repository specified -> JSON Response with error"""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_download,
                             user="user",
                             params=dict(device="ios-xrv-6-2-1"),
                             expect_errors=True)
        self.assertEqual(resp.status, "400 No repository specified")
        data = resp.json
        self.assertEqual({}, data)

    def test_incorrect_user(self):
        """Non-owner downloading files to repo-> JSON Response with error"""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_download,
                             user="Bob",
                             params=dict(device="ios-xrv-6-2-1",
                                         repository=merge_user_set(
                                                        "test", "testrepo")),
                             expect_errors=True)
        self.assertEqual(
            resp.status,
            "403 Only superusers may modify the contents of another "
            "user's repository")
        data = resp.json
        self.assertEqual({}, data)

    def test_no_netconf_in_device(self):
        """No netconf support -> raise Exception"""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_download,
                             user="test",
                             params=dict(device="ios-xrv",
                                         schemas=self.schema_list,
                                         repository=merge_user_set(
                                                        "test", "testrepo")),
                             expect_errors=True)
        self.assertEqual(
            resp.status,
            '400 Device "IOS XRv" is not marked as supporting NETCONF')
        data = resp.json
        self.assertEqual({
            'reply': 'Device "IOS XRv" is not marked as supporting NETCONF',
        }, data)

    @patch('ysnetconf.nconf.manager.connect')
    def test_netconf_monitoring_not_supported(self, m_connect):
        """Test raising Netconf monitoring not supported error"""
        clone_test_data(self.temp_path)
        m_manager = mock_manager(m_connect)
        p = PropertyMock(return_value={})
        type(m_manager).server_capabilities = p
        resp = self.app.post(self.url_download,
                             user='test',
                             params=dict(device="ios-xrv-6-2-1",
                                         schemas=self.schema_list,
                                         repository=merge_user_set(
                                                        "test", "testrepo")),
                             expect_errors=True)
        self.assertEqual(
            resp.status,
            '502 Device "IOS XRv 6.2.1" does not support the '
            "ietf-netconf-monitoring schema; you will have to obtain the "
            "requested schemas from another source.")
        data = resp.json
        self.assertEqual({}, data)

    @patch('ysnetconf.nconf.manager.connect')
    def test_exception_download_schemas_connect(self, m_connect):
        """Raise exception while trying to download"""
        clone_test_data(self.temp_path)
        m_manager = mock_manager(m_connect)
        p = PropertyMock(return_value=[self.nc_monitor])
        type(m_manager).server_capabilities = p
        m_connect.side_effect = Exception("It's a trap")
        resp = self.app.post(self.url_download,
                             user='test',
                             params=dict(device="ios-xrv-6-2-1",
                                         schemas=self.schema_list,
                                         repository=merge_user_set(
                                                        "test", "testrepo")),
                             expect_errors=True)
        self.assertEqual(resp.status, "500 Exception: It's a trap")
        data = resp.json
        self.assertEqual({}, data)

    DATASTRING_XML = u"""\
<rpc-reply message-id="urn:uuid:22a6f4b1-151c-4c45-aa05-fdef77d2f19a"
      xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"
      xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring">
module cisco-self-mgmt-test {
  namespace "http://cisco.com/yang/cisco-self-mgmt";
  prefix cisco-sfm;

  description
    "Copyright (c) 2016 by Cisco Systems, Inc."+
    "All rights reserved.";

  revision 2016-06-15 {
    description "TEST";
  }

  container netconf-yang {
    description
      "Still a test, with UTF-8 → ʜ𝒆𝔯𝕖";
  }
}
</data>
</rpc-reply>
"""

    @patch('ysnetconf.nconf.manager.connect')
    def test_download_schemas(self, m_connect):
        """Try and download schemas"""
        clone_test_data(self.temp_path)
        m_manager = mock_manager(m_connect)
        p = PropertyMock(return_value=[self.nc_monitor])
        type(m_manager).server_capabilities = p
        m_manager.dispatch.return_value = MagicMock(
                                            spec=ncclient.operations.GetReply)
        m_manager.dispatch.return_value.xml = self.DATASTRING_XML
        resp = self.app.post(self.url_download,
                             user='test',
                             params=dict(device="ios-xrv-6-2-1",
                                         schemas=self.schema_list_mgmt_test,
                                         repository=merge_user_set(
                                                        "test", "testrepo")),
                             expect_errors=False)
        self.assertEqual(resp.status, "200 OK")
        data = resp.json
        self.assertIn('reply', data)
        self.assertEqual(data['reply']['added'],
                         [['cisco-self-mgmt-test', '2016-06-15']])

    @patch('ysnetconf.nconf.manager.connect')
    def test_download_schemas_exception_dispatch(self, m_connect):
        """Raise exception while trying to do a m.dispatch"""
        clone_test_data(self.temp_path)
        m_manager = mock_manager(m_connect)
        p = PropertyMock(return_value=[self.nc_monitor])
        type(m_manager).server_capabilities = p
        m_manager.dispatch.side_effect = Exception("Error")
        resp = self.app.post(self.url_download,
                             user='test',
                             params=dict(device="ios-xrv-6-2-1",
                                         schemas=self.schema_list_mgmt_test,
                                         repository=merge_user_set(
                                                        "test", "testrepo")),
                             expect_errors=True)
        self.assertEqual(resp.status, "200 OK")
        data = resp.json
        self.assertIn('reply', data)
        self.assertEqual(data['reply']['errors'][1],
                         ['cisco-self-mgmt-test@2016-06-15.yang', "Error"])

    def tearDown(self):
        """Burn it all to the ground"""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)
