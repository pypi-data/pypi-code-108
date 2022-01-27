import unittest

from tcell_agent.instrumentation.better_ip_address import get_remote_address, get_reverse_proxy_header
from tcell_agent.tests.support.builders import ConfigurationBuilder
from tcell_agent.tests.support.context_library import ConfigContext


class BetterIpAddressTest(unittest.TestCase):
    def test_empty_env_get_remote_address(self):
        with ConfigContext(ConfigurationBuilder().build()):
            remote_address = get_remote_address({})

        self.assertEqual(remote_address, None)

    def test_empty_env_get_reverse_proxy_header_value(self):
        with ConfigContext(ConfigurationBuilder().build()):
            reverse_proxy_header_value = get_reverse_proxy_header({})

        self.assertEqual(reverse_proxy_header_value, None)

    def test_env_get_remote_address(self):
        with ConfigContext(ConfigurationBuilder().build()):
            remote_address = get_remote_address({"REMOTE_ADDR": "1.1.1.1"})

        self.assertEqual(remote_address, "1.1.1.1")

    def test_env_get_reverse_proxy_header(self):
        with ConfigContext(ConfigurationBuilder().build()):
            reverse_proxy_header_value = get_reverse_proxy_header({"X-Forwardard-For": "1.1.1.1",
                                                                   "HTTP_X_FORWARDED_FOR": "2.2.2.2"})

        self.assertEqual(reverse_proxy_header_value, "2.2.2.2")
