from pytest import raises

from metadatadb_driver_interface.utils import parse_config


def test_metadatadb_expects_plugin():
    from metadatadb_driver_interface.plugin import AbstractPlugin
    with raises(TypeError):
        AbstractPlugin()


def test_metadatadb_expcects_subclassed_plugin():
    from metadatadb_driver_interface.plugin import AbstractPlugin

    class NonSubclassPlugin():
        pass

    plugin = NonSubclassPlugin()
    with raises(TypeError):
        AbstractPlugin(plugin)


def test_parse_config():
    config = parse_config('./tests/config.ini')
    assert config['module'] == 'elasticsearch'
    assert config['db.hostname'] == 'localhost'
