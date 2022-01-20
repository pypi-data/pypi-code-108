import unittest2 as unittest

from ysdevices import YSDeviceProfile


class TestDevicePlugin(unittest.TestCase):
    """Validate the GnmiPlugin for YSDeviceProfile."""

    def test_plugin_properties(self):
        """Make sure the expected plugin properties are present."""
        profile = YSDeviceProfile()
        self.assertFalse(profile.gnmi.enabled)
        self.assertEqual('iosxe', profile.gnmi.platform)
        self.assertEqual(50052, profile.gnmi.port)

    # TODO test_check_reachability
