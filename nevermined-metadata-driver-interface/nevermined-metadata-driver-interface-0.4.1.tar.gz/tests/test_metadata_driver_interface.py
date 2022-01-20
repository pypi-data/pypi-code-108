from pytest import raises

from metadata_driver_interface.driver_interface import DriverInterface
from metadata_driver_interface.utils import parse_config


def test_driver_expects_plugin():
    from metadata_driver_interface.data_plugin import AbstractPlugin
    with raises(TypeError):
        AbstractPlugin()


def test_driver_expcects_subclassed_plugin():
    from metadata_driver_interface.data_plugin import AbstractPlugin

    class NonSubclassPlugin:
        pass

    plugin = NonSubclassPlugin()
    with raises(TypeError):
        AbstractPlugin(plugin)


def test_parse_config():
    config = parse_config('./tests/config.ini')
    assert config['azure.location'] == 'westus'


def test_driver_instances():
    osm = DriverInterface('http://www.example.com')
    assert osm.data_plugin.type() == 'On premise'
