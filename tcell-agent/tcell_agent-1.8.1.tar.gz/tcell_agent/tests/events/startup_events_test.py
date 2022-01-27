import unittest

from mock import patch

from tcell_agent.events.startup_events import get_startup_events
from tcell_agent.tests.support.builders import ConfigurationBuilder
from tcell_agent.tests.support.context_library import ConfigContext


class TestPackage(object):
    def __init__(self, key, version):
        self.key = key
        self.version = version


class GetStartupEventsTest(unittest.TestCase):
    def test_get_startup_events(self):
        config = ConfigurationBuilder().update_attribute(
            "log_directory", "log-directory"
        ).update_attribute(
            "allow_payloads", True
        ).update_attribute(
            "reverse_proxy", True
        ).update_attribute(
            "hmac_key", "hmac-key"
        ).update_attribute(
            "reverse_proxy_ip_address_header", "X-Forwarded-For"
        ).update_attribute(
            "config_filename", "tcell_agent.config"
        ).build()
        packages = [TestPackage("tcell-agent", "1.0.0")]

        with patch("tcell_agent.events.startup_events.get_packages",
                   return_value=packages) as patched_get_packages:
            with ConfigContext(config):
                initial_events = get_startup_events()

            self.assertTrue(patched_get_packages.called)
            self.assertEqual(
                initial_events,
                [
                    {"event_type": "server_agent_packages", "packages": [{"n": "tcell-agent", "v": "1.0.0"}]},
                    {"event_type": "app_config_setting", "package": "tcell", "section": "config", "name": "native_lib_loaded", "value": "true"}
                ])
