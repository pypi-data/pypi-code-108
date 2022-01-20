# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
import os.path
import unittest2 as unittest
from mock import patch, MagicMock
import ncclient.operations

from .. import nconf
from yangsuite.paths import set_base_path
from .utilities import mock_manager


class TestNConfLockUnlock(unittest.TestCase):
    """Tests manual Locking, Unlocking and session creation."""

    testdir = os.path.join(os.path.dirname(__file__), 'data')

    @classmethod
    def setUpClass(cls):
        """Function called before starting test execution in this class."""
        set_base_path(cls.testdir)

    def setUp(self):
        """Function called before each test case."""
        key = nconf.SessionKey('test', 'IOS XRv 6.2.1')
        if key in nconf.NetconfSession.instances:
            nconf.NetconfSession.instances[key].disconnect()
            del nconf.NetconfSession.instances[key]

    @patch('ysnetconf.nconf.manager.connect')
    def test_lock_datastore(self, m_connect):
        """Test lock_datastore API."""
        m_manager = mock_manager(m_connect)
        m_manager.lock.return_value = MagicMock(
            spec=ncclient.operations.RPCReply)
        key = nconf.SessionKey('test', 'IOS XRv 6.2.1')
        session = nconf.NetconfSession.get(key)
        session.manager = m_manager
        result = nconf.lock_datastore(key, 'candidate', 30)
        self.assertEqual(result['reply'], 'Datastore Locked')

    @patch('ysnetconf.nconf.manager.connect')
    def test_lock_datastore_negative(self, m_connect):
        """Test lock_datastore API for failure conditions."""
        m_manager = mock_manager(m_connect)
        m_manager.lock.return_value = MagicMock(
            spec=ncclient.operations.RPCReply)

        # when device doen't support netconf.
        key = nconf.SessionKey('test', 'IOS XRv')
        result = nconf.lock_datastore(key, 'candidate', 30)
        self.assertEqual(result['reply'],
                         "The device doesn't support netconf")

        # when lock operation fails
        key = nconf.SessionKey('test', 'IOS XRv 6.2.1')
        m_manager.lock.return_value.ok = False
        session = nconf.NetconfSession.get(key)
        session.manager = m_manager
        result = nconf.lock_datastore(key, 'candidate', 30)
        self.assertEqual(result['reply'], 'Lock failed')

        # Locks fails if the session is None
        session.manager = None
        result = nconf.lock_datastore(key, 'candidate', 30)
        self.assertEqual(
            result['reply'],
            'No active session found. Start a session to acquire lock')

    @patch('ysnetconf.nconf.manager.connect')
    def test_unlock_datastore(self, m_connect):
        """Tests unlock_datastore API."""
        m_manager = mock_manager(m_connect)
        m_manager.unlock.return_value = MagicMock(
            spec=ncclient.operations.RPCReply)
        key = nconf.SessionKey('test', 'IOS XRv 6.2.1')
        nconf_session = nconf.NetconfSession.get(key)
        nconf_session.manager = m_manager
        nconf_session.locked_datastores.append('candidate')
        result = nconf.unlock_datastore(key, 'candidate')
        self.assertEqual(result['reply'], 'Datastore unlocked successfully')

    @patch('ysnetconf.nconf.manager.connect')
    def test_unlock_datastore_negative(self, m_connect):
        """Tests unlock_datastore API for failure conditions."""
        m_manager = mock_manager(m_connect)
        m_manager.unlock.return_value = MagicMock(
            spec=ncclient.operations.RPCReply)

        # when device doen't support netconf.
        key = nconf.SessionKey('test', 'IOS XRv')
        result = nconf.unlock_datastore(key, 'candidate')
        self.assertEqual(result['reply'], "The device doesn't support netconf")

        key = nconf.SessionKey('test', 'IOS XRv 6.2.1')
        nconf_session = nconf.NetconfSession.get(key)
        nconf_session.manager = m_manager
        nconf_session.locked_datastores.append('candidate')

        # when unlock return value is false.
        m_manager.unlock.return_value.ok = False
        result = nconf.unlock_datastore(key, 'candidate')
        error = m_manager.unlock.return_value.error.tag
        self.assertEqual(result['reply'],
                         'Unlock failed with ' + error + ' error')

        # when target selected is not locked
        result = nconf.unlock_datastore(key, 'running')
        self.assertEqual(result['reply'], 'Already Unlocked')

        # if the session is none.
        nconf_session.manager = None
        result = nconf.unlock_datastore(key, 'candidate')
        self.assertEqual(result['reply'], 'No active session found')

    @patch('ysnetconf.nconf.manager.connect')
    def test_start_session(self, m_connect):
        """Tests start_session API for success condition."""
        mock_manager(m_connect)

        key = nconf.SessionKey('test', 'IOS XRv 6.2.1')
        result = nconf.start_session(key)
        m_connect.assert_called_once()
        self.assertTrue(result)

    @patch('ysnetconf.nconf.manager.connect')
    def test_end_session(self, m_connect):
        """Tests end_session API for success condition."""
        m_manager = mock_manager(m_connect)
        key = nconf.SessionKey('test', 'IOS XRv 6.2.1')
        nconf_session = nconf.NetconfSession.get(key)
        nconf_session.manager = m_manager
        result = nconf.end_session(key)
        self.assertTrue(result)
