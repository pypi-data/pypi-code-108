from __future__ import print_function

import unittest

import pytest
from mock import patch


from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.flaskinst.check_agent_startup import (
    start_agent
)
from tcell_agent.tests.support.builders import ConfigurationBuilder

from flask import __version__


@pytest.mark.flask
class CheckAgentStartupTest(unittest.TestCase):
    def setUp(self):
        ConfigurationBuilder().set_config()

    def test_agent_ignores_startup_info_when_disabled(self):
        with patch.object(TCellAgent, "startup", return_value=False) as patched_startup:
            with patch("tcell_agent.instrumentation.flaskinst.routes.report_routes", return_value=None) as patched_report_routes:
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    start_agent()
                    self.assertTrue(patched_startup.called)
                    self.assertFalse(patched_report_routes.called)
                    self.assertFalse(patched_send.called)

    def test_agent_sends_startup_info_start_agent(self):
        with patch.object(TCellAgent, "startup", return_value=True) as patched_startup:
            with patch("tcell_agent.instrumentation.flaskinst.routes.report_routes", return_value=None) as patched_report_routes:
                start_agent()
                self.assertTrue(patched_report_routes.called)
                self.assertTrue(patched_startup.called)
