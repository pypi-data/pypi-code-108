from unittest import IsolatedAsyncioTestCase

from eyja.hubs.plugin_hub import PluginHub


class PluginHubTest(IsolatedAsyncioTestCase):
    async def test_load_plugin(self):
        await PluginHub.init(
            plugins=[
                'tests.packages.eyja_test_pyson_db',
            ]
        )

        self.assertIn('pyson-test', PluginHub.plugins())
