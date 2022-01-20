# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Tests for utility.nconf module."""

import os.path
import unittest2 as unittest
from mock import patch, MagicMock
import ncclient.operations

from .. import nconf
from yangsuite.paths import set_base_path

from .utilities import mock_manager


@patch('ysnetconf.nconf.manager.connect')
class TestLockRetry(unittest.TestCase):
    """Tests for try_lock module functions."""

    testdir = os.path.join(os.path.dirname(__file__), 'data')

    @classmethod
    def setUpClass(cls):
        """Function called before starting test execution in this class."""
        set_base_path(cls.testdir)

    def mock_session(self, m_connect, ok=True, error_tag=None):
        session = nconf.NetconfSession.get(nconf.SessionKey('test',
                                                            'miott-csr'))
        m_manager = mock_manager(m_connect)
        m_manager.lock.return_value = MagicMock(
            spec=ncclient.operations.RPCReply)
        m_manager.lock.return_value.ok = ok
        if error_tag:
            m_manager.lock.return_value.error.tag = error_tag
        session.manager = m_manager
        return session

    def tearDown(self):
        key = nconf.SessionKey('test', 'miott-csr')
        if key in nconf.NetconfSession.instances:
            nconf.NetconfSession.instances[key].disconnect()
            del nconf.NetconfSession.instances[key]

    def test_try_lock_passed(self, m_connect):
        session = self.mock_session(m_connect)
        ret = nconf.try_lock(session, 'candidate', 5, 1)
        session.manager.lock.assert_called_once()
        self.assertTrue(ret)

    def test_try_lock_lock_denied(self, m_connect):
        session = self.mock_session(m_connect, False, 'lock-denied')
        nconf.try_lock(session, 'candidate', 5, 1)
        self.assertEqual(session.manager.lock.call_count, 5)
        self.assertEqual(session.message_log.popleft(), "RETRYING LOCK - 1")
        self.assertEqual(session.message_log.pop(),
                         "ERROR - LOCKING FAILED. RETRY TIMER EXCEEDED!!!")

    def test_try_lock_resource_denied(self, m_connect):
        session = self.mock_session(m_connect, False, 'resource-denied')
        nconf.try_lock(session, 'candidate', 5, 1)
        self.assertEqual(session.manager.lock.call_count, 5)
        self.assertEqual(session.message_log.popleft(), "RETRYING LOCK - 1")
        self.assertEqual(session.message_log.pop(),
                         "ERROR - LOCKING FAILED. RETRY TIMER EXCEEDED!!!")

    def test_try_lock_in_use(self, m_connect):
        session = self.mock_session(m_connect, False, 'in-use')
        nconf.try_lock(session, 'candidate', 5, 1)
        self.assertEqual(session.manager.lock.call_count, 5)
        self.assertEqual(session.message_log.popleft(), "RETRYING LOCK - 1")
        self.assertEqual(session.message_log.pop(),
                         "ERROR - LOCKING FAILED. RETRY TIMER EXCEEDED!!!")

    def test_try_lock_negative(self, m_connect):
        session = self.mock_session(m_connect, False, 'access-denied')
        ret = nconf.try_lock(session, 'candidate', 5, 1)
        session.manager.lock.assert_called_once()
        self.assertEqual(session.message_log.popleft(),
                         "ERROR - CANNOT ACQUIRE LOCK - {0}".format(
                             session.manager.lock.return_value.error.tag))
        self.assertFalse(ret)

    def test_try_lock_timer_exceed(self, m_connect):
        session = self.mock_session(m_connect, False, 'lock-denied')
        ret = nconf.try_lock(session, 'candidate', 5, 1)
        self.assertEqual(session.manager.lock.call_count, 5)
        self.assertEqual(session.message_log.pop(),
                         "ERROR - LOCKING FAILED. RETRY TIMER EXCEEDED!!!")
        self.assertFalse(ret)
