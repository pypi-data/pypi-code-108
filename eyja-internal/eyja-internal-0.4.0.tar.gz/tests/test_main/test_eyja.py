import os

from unittest import IsolatedAsyncioTestCase

from eyja.main import Eyja
from eyja.hubs.config_hub import ConfigHub
from eyja.hubs.plugin_hub import PluginHub
from eyja.hubs.data_hub import DataHub


class EyjaTest(IsolatedAsyncioTestCase):
    str_config = '''
        storages:
    '''

    dict_config = {
        'storages': {}
    }

    file_config = 'tests/config/simple_test.yml'

    async def test_eyja_init_without_config(self):
        await Eyja.reset()
        await Eyja.init()

        self.assertFalse(Eyja.is_initialized())

    async def test_eyja_init_with_str_config(self):
        await Eyja.reset()
        await Eyja.init(config=self.str_config)

        self.assertTrue(Eyja.is_initialized())

    async def test_eyja_init_with_dict_config(self):
        await Eyja.reset()
        await Eyja.init(config=self.dict_config)

        self.assertTrue(Eyja.is_initialized())

    async def test_eyja_init_with_file_config(self):
        await Eyja.reset()
        await Eyja.init(config_file=os.path.join(os.getcwd(), self.file_config))

        self.assertTrue(Eyja.is_initialized())
