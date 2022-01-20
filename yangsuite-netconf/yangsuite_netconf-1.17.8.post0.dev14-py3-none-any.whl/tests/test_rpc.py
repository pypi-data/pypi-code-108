# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Tests ysnetconf/views/rpc.py."""
from __future__ import unicode_literals
import json
import logging
import os.path
import os
import tempfile
import shutil

try:
    # Django 2.x
    from django.urls import reverse
except ImportError:
    # Django 1.x
    from django.core.urlresolvers import reverse

from django_webtest import WebTest
from yangsuite.paths import set_base_path
from mock import patch, MagicMock, PropertyMock
import lxml.etree as et
import ncclient.operations
from ncclient.transport.errors import SSHError
from .utilities import (
    canned_input_data,
    canned_output_str,
    canned_output_data,
    mock_manager,
)
from ysnetconf.nconf import (
    NetconfSession,
    SessionKey,
    CAP_CANDIDATE,
    CAP_STARTUP,
)


def clone_test_data(new_location):
    """Copy test data and set new base path."""
    if os.path.exists(new_location):
        shutil.rmtree(new_location)
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'data'),
                    new_location)
    set_base_path(new_location)


testdir = os.path.join(os.path.dirname(__file__), 'data')


class TestRunResultPage(WebTest):
    """Render runresult.html page."""

    def setUp(self):
        """Function that will be called before the start of each test."""
        set_base_path(testdir)

    def test_access_restriction(self):
        """No user --> login page; logged in --> runresult.html."""
        url = reverse('netconf:runresult')

        resp = self.app.get(url)
        self.assertRedirects(resp, "/accounts/login/?next=" + url)

        resp = self.app.get(url, user='test')
        self.assertTemplateUsed(resp, 'ysnetconf/runresult.html')


class TestGetTask(WebTest):
    """Test the get_task view function."""

    csrf_checks = False

    def setUp(self):
        """Function that will be called before the start of each test."""
        self.url_get_rpc = reverse('netconf:gettaskrpc')
        set_base_path(testdir)
        self.temp_path = tempfile.mkdtemp()
        self.maxDiff = None

    def test_reject_run(self):
        """The 'run' gentype is not usable through this API."""
        resp = self.app.post(self.url_get_rpc,
                             user='test',
                             params=dict(name="getMgmt",
                                         category='default'),
                             expect_errors=True)
        self.assertEqual(resp.status_code, 400)

    def test_no_name_exception(self):
        """Incorrect task name specified -> TaskNotFoundException."""
        resp = self.app.post(self.url_get_rpc,
                             user='test',
                             params=dict(name='Blah',
                                         category='default',
                                         gentype='raw'),
                             expect_errors=True)
        self.assertEqual(resp.status,
                         '500 Task "Blah" does not exist')
        data = resp.json
        self.assertEqual({}, data)

    def test_success_custom(self):
        """Successful loading of a custom task."""
        resp = self.app.post(self.url_get_rpc,
                             user='test',
                             params=dict(name='custom',
                                         category='default',
                                         dsstore='running',
                                         prefix_namespaces='always',
                                         gentype='raw'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertEqual(canned_output_data('custom.json'), data)

    def test_success_basic(self):
        """Successful loading of a typical task with 'basic' gentype."""
        resp = self.app.post(self.url_get_rpc,
                             user='test',
                             params=dict(name="getMgmt",
                                         category='default',
                                         dsstore="running",
                                         prefixes="always",
                                         gentype="basic"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertEqual(canned_output_data('getMgmt.basic.json'), data)

    def test_success_basic_minimal_prefix(self):
        """Successful loading a task with 'basic' gentype 'minimal' prefix."""
        resp = self.app.post(self.url_get_rpc,
                             user='test',
                             params=dict(name="getMgmt",
                                         category='default',
                                         dsstore="running",
                                         prefixes="minimal",
                                         gentype="basic"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertEqual(canned_output_data('getMgmt.minimal.json'), data)

    def test_success_basic_default_prefix(self):
        """Successful loading a task with 'basic' gentype default prefix."""
        resp = self.app.post(self.url_get_rpc,
                             user='test',
                             params=dict(name="getMgmt",
                                         category='default',
                                         dsstore="running",
                                         gentype="basic"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertEqual(canned_output_data('getMgmt.minimal.json'), data)

    def tearDown(self):
        """Burn it all to the ground."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)


class TestClearRPCResults(WebTest):
    """Test the clear_rpc_result function."""

    csrf_checks = False

    def setUp(self):
        """Function that will be called before the start of each test."""
        self.url_get = reverse('netconf:clearrpc')
        set_base_path(testdir)

    def test_clear(self):
        """Send context -> get back JSON response with done."""
        session = NetconfSession.get(SessionKey('test', 'ios-xrv-6-2-1'))
        session.log("Hello world!")
        self.assertGreater(len(session.message_log), 0)
        resp = self.app.post(self.url_get,
                             user='test',
                             params=json.dumps({'device': 'ios-xrv-6-2-1'}),
                             expect_errors=False)
        data = resp.json
        self.assertIn('status', data)
        self.assertEqual('done', data['status'])

        self.assertEqual(0, len(session.message_log))


class TestRunRPC(WebTest):
    """Test run_rpc function."""

    csrf_checks = False

    def setUp(self):
        """Function that will be called before the start of each test."""
        self.url_run = reverse('netconf:runrpc')
        set_base_path(testdir)
        self.temp_path = tempfile.mkdtemp()

    def test_device_none(self):
        """No device specified -> JSON response with 'No device profile'."""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_run,
                             user='test',
                             params=json.dumps({'rpcs': ''}),
                             expect_errors=True)
        data = resp.json
        self.assertIn('reply', data)
        self.assertEqual('No device profile', data['reply'])

    def test_device_no_netconf(self):
        """Device has no NETCONF support -> JSON response with error."""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_run,
                             user='test',
                             params=json.dumps(dict(rpcs="",
                                                    device="ios-xrv")),
                             expect_errors=True)
        data = resp.json
        self.assertIn('reply', data)
        self.assertEqual(
            'Device "IOS XRv" is not marked as supporting NETCONF',
            data['reply'])

    def test_task_raise_exception(self):
        """Raise TaskException."""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_run,
                             user='test',
                             params=json.dumps(dict(rpcs="",
                                                    task='blah',
                                                    category='default',
                                                    dsstore='candidate',
                                                    device="ios-xrv-6-2-1")),
                             expect_errors=True)
        data = resp.json
        self.assertIn('error', data)
        self.assertEqual('Task "blah" does not exist', data['error'])

    TASKDATA = [canned_input_data('get_config_if.basic.json')]

    @patch('ysnetconf.nconf.manager.connect')
    def test_nconf_gen_task_api_response(self, m_connect):
        """Pass valid params: get back JSON success."""
        clone_test_data(self.temp_path)
        m_manager = mock_manager(m_connect)
        m_manager.get_config.return_value = MagicMock(
            spec=ncclient.operations.GetReply)
        m_manager.get_config.return_value.data_ele = et.Element("gotten")
        resp = self.app.post(self.url_run,
                             user='test',
                             params=json.dumps(dict(name='getMgmt',
                                                    task='getMgmt',
                                                    category='default',
                                                    dsstore='running',
                                                    device="ios-xrv-6-2-1")),
                             expect_errors=False)
        data = resp.json
        self.assertIn('reply', data)
        self.assertNotIn("error", data)
        m_manager.get_config.assert_called()

    def test_task_no_rpcs(self):
        """Don't pass rpcs -> get back JSON response with error."""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_run,
                             user='test',
                             params=json.dumps(dict(name='getMgmt',
                                                    category='default',
                                                    dsstore='running',
                                                    device="ios-xrv-6-2-1")),
                             expect_errors=True)
        data = resp.json
        self.assertIn('reply', data)
        self.assertEqual('No RPC sent', data['reply'])

    GET_CONFIG_XML = canned_output_str('get_config_ocif.raw.xml')
    GET_CONFIG_NO_PREFIX_XML = canned_output_str(
        'get_config_ocif_noprefix.raw.xml')

    @patch('ysnetconf.nconf.manager.connect')
    def test_custom_multiple_rpc(self, m_connect):
        """Custom rpcs -> get back JSON response with success."""
        clone_test_data(self.temp_path)
        m_manager = mock_manager(m_connect)
        m_manager.dispatch.return_value = MagicMock(
            spec=ncclient.operations.GetReply)
        m_manager.dispatch.return_value.data_ele = et.Element("gotten")
        rpcs = self.GET_CONFIG_XML + \
            self.GET_CONFIG_NO_PREFIX_XML + \
            self.GET_CONFIG_XML
        resp = self.app.post(self.url_run,
                             user='test',
                             params=json.dumps(dict(rpcs=rpcs,
                                                    custom=self.GET_CONFIG_XML,
                                                    device="ios-xrv-6-2-1")),
                             expect_errors=False)
        data = resp.json
        self.assertIn('reply', data)
        self.assertNotIn("error", data)
        m_manager.dispatch.assert_called()

    @patch('ysnetconf.nconf.manager.connect')
    def test_task_custom(self, m_connect):
        """Custom rpcs -> get back JSON response with success."""
        clone_test_data(self.temp_path)
        m_manager = mock_manager(m_connect)
        m_manager.dispatch.return_value = MagicMock(
            spec=ncclient.operations.GetReply)
        m_manager.dispatch.return_value.data_ele = et.Element("gotten")
        resp = self.app.post(self.url_run,
                             user='test',
                             params=json.dumps(dict(rpcs=self.GET_CONFIG_XML,
                                                    custom=self.GET_CONFIG_XML,
                                                    device="ios-xrv-6-2-1")),
                             expect_errors=False)
        data = resp.json
        self.assertIn('reply', data)
        self.assertNotIn("error", data)
        m_manager.dispatch.assert_called()

    @patch('ysnetconf.nconf.manager.connect')
    def test_task_only_rpcs(self, m_connect):
        """Post only rpcs -> get back JSON response."""
        clone_test_data(self.temp_path)
        m_manager = mock_manager(m_connect)
        m_manager.get_config.return_value = MagicMock(
            spec=ncclient.operations.GetReply)
        m_manager.get_config.return_value.data_ele = et.Element("gotten")
        resp = self.app.post(self.url_run,
                             user='test',
                             params=json.dumps(dict(rpcs=self.TASKDATA,
                                                    device="ios-xrv-6-2-1")),
                             expect_errors=False)
        data = resp.json
        self.assertIn('reply', data)
        self.assertNotIn("error", data)
        m_manager.get_config.assert_called()

    def tearDown(self):
        """Burn it all to the ground."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)
        key = SessionKey('test', 'ios-xrv-6-2-1')
        if key in NetconfSession.instances:
            NetconfSession.instances[key].disconnect()
            del NetconfSession.instances[key]


class TestGetRPC(WebTest):
    """Test the get_rpc function."""

    csrf_checks = False

    def setUp(self):
        """Function that will be called before the start of each test."""
        self.url_get = reverse('netconf:getrpc')
        set_base_path(testdir)
        self.temp_path = tempfile.mkdtemp()

    def test_wrong_params(self):
        """Check for handling of valid JSON with the wrong parameters."""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_get,
                             user='test',
                             params=json.dumps(dict(name='getMgmt',
                                                    category='default',
                                                    dsstore='running',
                                                    device="ios-xrv-6-2-1")),
                             expect_errors=False)
        data = resp.json
        self.assertIn('reply', data)
        self.assertEqual("Failed to generate RPC", data['reply'])

    def test_canned_get_config(self):
        """Test get-config basic format."""
        resp = self.app.post(
            self.url_get, user='test',
            params=json.dumps({
                "gentype": "basic",
                'prefix_namespaces': 'always',
                "cfgd": canned_input_data('get_config_ocif.cfgd.json')}))
        data = resp.json
        self.assertEqual(canned_output_str('get_config_ocif.basic.filter.xml'),
                         data['reply'])

    def tearDown(self):
        """Burn it all to the ground."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)


class TestNetconfPage(WebTest):
    """Render main NETCONF page via get_yang."""

    csrf_checks = False

    def setUp(self):
        """Function that will be called before the start of each test."""
        self.url_get = reverse('netconf:getyang')
        set_base_path(testdir)
        self.temp_path = tempfile.mkdtemp()

    def test_get(self):
        """Test render get."""
        resp = self.app.get(self.url_get, user='test')
        self.assertTemplateUsed(resp, 'ysnetconf/netconf.html')

    def test_post(self):
        """Test render post."""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_get,
                             user='test',
                             expect_errors=False)
        self.assertTemplateUsed(resp, 'ysnetconf/netconf.html')

    def tearDown(self):
        """Burn it all to the ground."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)


class TestLockUnlockDatastore(WebTest):
    """Test the lock_unlock_datastore view function."""

    csrf_checks = False

    def setUp(self):
        self.url = reverse('netconf:lockunlockdatastore')
        set_base_path(testdir)

    def tearDown(self):
        key = SessionKey('test', 'ios-xrv-6-2-1')
        if key in NetconfSession.instances:
            NetconfSession.instances[key].disconnect()
            del NetconfSession.instances[key]

    def test_negative_missing_args(self):
        """Mandatory args missing --> error."""
        resp = self.app.post(self.url)
        self.assertRedirects(resp, "/accounts/login/?next=" + self.url)

        resp = self.app.post(self.url, user='test', expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 No device profile',
                         resp.status)

        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv-6-2-1'}),
                             expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 Missing mandatory parameter dsstore',
                         resp.status)

        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv-6-2-1',
                                                'dsstore': 'running'}),
                             expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 Missing mandatory parameter lock',
                         resp.status)

        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv-6-2-1',
                                                'dsstore': 'running',
                                                'lock': True}),
                             expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 Missing mandatory parameter retry_timer',
                         resp.status)

    def test_negative_invalid_args(self):
        """Various malformed arguments."""
        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'foobar'}),
                             expect_errors=True)
        self.assertEqual(404, resp.status_code)
        self.assertEqual('404 No such device',
                         resp.status)

        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv'}),
                             expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 Device "IOS XRv" is not marked as '
                         'supporting NETCONF', resp.status)

        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv-6-2-1',
                                                'dsstore': 'running',
                                                'lock': True,
                                                'retry_timer': 'hello'}),
                             expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 Invalid retry_timer value', resp.status)

    @patch('ysnetconf.nconf.lock_datastore')
    def test_lock_success(self, mock_lock):
        """Successful locking."""
        mock_lock.return_value = {'reply': 'Datastore Locked'}

        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv-6-2-1',
                                                'dsstore': 'running',
                                                'lock': True,
                                                'retry_timer': 45}))
        self.assertEqual(200, resp.status_code)
        self.assertEqual("Datastore Locked", resp.json['resp'])

    @patch('ysnetconf.nconf.unlock_datastore')
    def test_unlock_success(self, mock_unlock):
        """Successful unlocking."""
        mock_unlock.return_value = {'reply': 'Datastore unlocked successfully'}

        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv-6-2-1',
                                                'dsstore': 'running',
                                                'lock': False,
                                                'retry_timer': 45}))
        self.assertEqual(200, resp.status_code)
        self.assertEqual("Datastore unlocked successfully", resp.json['resp'])


class TestStartEndSession(WebTest):
    """Test the start_end_session view function."""

    csrf_checks = False

    def setUp(self):
        self.url = reverse('netconf:startendsession')
        set_base_path(testdir)

    def tearDown(self):
        key = SessionKey('test', 'ios-xrv-6-2-1')
        if key in NetconfSession.instances:
            NetconfSession.instances[key].disconnect()
            del NetconfSession.instances[key]

    def test_negative_missing_args(self):
        """Mandatory args missing --> error."""
        resp = self.app.post(self.url)
        self.assertRedirects(resp, "/accounts/login/?next=" + self.url)

        resp = self.app.post(self.url, user='test', expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 No device profile',
                         resp.status)

        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv-6-2-1'}),
                             expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 Invalid session value', resp.status)

        # rpctimeout can be omitted in which case it defaults

    def test_negative_invalid_args(self):
        """Various malformed arguments."""
        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'foobar'}),
                             expect_errors=True)
        self.assertEqual(404, resp.status_code)
        self.assertEqual('404 No such device',
                         resp.status)

        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv'}),
                             expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 Device "IOS XRv" is not marked as '
                         'supporting NETCONF', resp.status)

        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv-6-2-1',
                                                'session': 'start',
                                                'rpctimeout': 'hello'}),
                             expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 Invalid rpctimeout value', resp.status)

    @patch('ysnetconf.nconf.start_session')
    def test_start_success(self, mock_start):
        """Successful session start."""
        mock_start.return_value = True
        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv-6-2-1',
                                                'session': 'start'}))
        self.assertEqual(200, resp.status_code)
        self.assertEqual(True, resp.json['reply'])

    @patch('ysnetconf.nconf.end_session')
    def test_end_success(self, mock_end):
        """Successful session end."""
        mock_end.return_value = True
        resp = self.app.post(self.url, user='test',
                             params=json.dumps({'device': 'ios-xrv-6-2-1',
                                                'session': 'end'}))
        self.assertEqual(200, resp.status_code)
        self.assertEqual(True, resp.json['reply'])


class TestListDatastores(WebTest):
    """Test the list_datastores view function."""

    def setUp(self):
        self.url = reverse('netconf:datastores')
        set_base_path(testdir)

    def tearDown(self):
        key = SessionKey('test', 'ios-xrv-6-2-1')
        if key in NetconfSession.instances:
            NetconfSession.instances[key].disconnect()
            del NetconfSession.instances[key]

    def test_negative_invalid_params(self):
        resp = self.app.get(self.url)
        self.assertRedirects(resp, "/accounts/login/?next=" + self.url)

        resp = self.app.get(self.url, user='test', expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 No device profile', resp.status)

        resp = self.app.get(self.url, user='test',
                            params={'device': 'foobar'},
                            expect_errors=True)
        self.assertEqual(404, resp.status_code)
        self.assertEqual('404 No such device', resp.status)

        resp = self.app.get(self.url, user='test',
                            params={'device': 'ios-xrv'},
                            expect_errors=True)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('400 Device "IOS XRv" is not marked as '
                         'supporting NETCONF', resp.status)

    @patch('ysnetconf.nconf.manager.connect')
    def test_negative_connection_refused(self, m_connect):
        m_connect.side_effect = SSHError()

        resp = self.app.get(self.url, user='test',
                            params={'device': 'ios-xrv-6-2-1',
                                    'operation': 'edit-config'},
                            expect_errors=True)
        self.assertEqual(
            '502 SSH connection refused by device "IOS XRv 6.2.1"',
            resp.status)

    @patch('ysnetconf.nconf.manager.connect')
    def test_success(self, m_connect):
        m_manager = mock_manager(m_connect)
        type(m_manager).server_capabilities = PropertyMock(return_value=[
            CAP_CANDIDATE,
            CAP_STARTUP,
            # not CAP_WRITABLE_RUN
        ])

        resp = self.app.get(self.url, user='test',
                            params={'device': 'ios-xrv-6-2-1'},
                            expect_errors=True)
        self.assertEqual('200 OK', resp.status)
        data = resp.json
        self.assertEqual(['candidate', 'running', 'startup'],
                         data['get-config'])
        self.assertEqual(['candidate'], data['edit-config'])

        resp = self.app.get(self.url, user='test',
                            params={'device': 'ios-xrv-6-2-1',
                                              'list_all': True},
                            expect_errors=True)
        data = resp.json
        self.assertEqual(set(data['all_datastores']),
                         set(['running', 'candidate', 'startup']))


class TestSetLog(WebTest):
    """Test the set_log view function."""

    csrf_checks = False

    def setUp(self):
        self.url = reverse('netconf:setlog')
        set_base_path(testdir)

    def test_login_required(self):
        resp = self.app.get(self.url)
        self.assertRedirects(resp, "/accounts/login/?next=" + self.url)

    def test_set_log(self):
        """Log level defaults to INFO and can be set to INFO or DEBUG."""
        logger = logging.getLogger('ncclient')
        self.assertEqual(logger.getEffectiveLevel(), logging.INFO)

        resp = self.app.post(self.url, user='test',
                             params={'loglevel': 'debug'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual(logger.getEffectiveLevel(), logging.DEBUG)

        # Can't actually set any less verbose than INFO
        resp = self.app.post(self.url, user='test',
                             params={'loglevel': 'warning'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual(logger.getEffectiveLevel(), logging.INFO)
