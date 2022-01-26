"""
Setup fixtures for pytest
This file is automatically loaded in every test by pytest.
See:
https://docs.pytest.org/en/6.2.x/fixture.html#conftest-py-sharing-fixtures-across-multiple-files
"""

from datetime import date
import pytest
from ntbk.config import Config
from ntbk.filesystem import Filesystem
from ntbk.dispatcher import Dispatcher
from ntbk.entities.logs import LogDate
from ntbk.entities.templates import Template
from ntbk.entities.collections import CollectionFile

# 2021-12-30
FAKE_TODAY = date(2021, 12, 30)

@pytest.fixture(name='config')
def config_fixture(tmp_path):
    """Return a test Config instance"""
    conf_file = tmp_path / '.config/ntbk/ntbk.yml'
    conf = {
        'ntbk_dir': str(tmp_path),
        'default_templates': {},
        'template_vars': {}
    }
    return Config(conf, conf_file)

@pytest.fixture(name='filesystem')
def filesystem_fixture(config, mocker):
    """Return a test Filesystem instance"""
    fs_obj = Filesystem(config)
    mocker.patch.object(fs_obj, 'open_file_in_editor', autospec=True)
    return fs_obj

@pytest.fixture(name='dispatcher')
def dispatcher_fixture(config, filesystem):
    """Return a test Dispatcher instance"""
    return Dispatcher(config, filesystem)

@pytest.fixture(name='ntbk_dir')
def ntbk_dir_fixture(filesystem):
    """Return ntbk base Path for testing"""
    return filesystem.get_notebook_base_path()

@pytest.fixture(name='log_date')
def log_date_fixture(config, filesystem):
    """Return a test LogDate instance"""
    date_obj = date(2021, 1, 1)
    return LogDate(config, filesystem, date_obj)

@pytest.fixture(name='collection_file')
def collection_file_fixture(config, filesystem):
    """Return a test CollectionFile instance"""
    collection_name = 'test-collection'
    file_name = 'index'
    collection_file =  CollectionFile(config, filesystem, collection_name, file_name)
    collection_file.get_collection().get_path().mkdir(parents=True)
    return collection_file

@pytest.fixture(name='template_factory')
def template_factory_fixture(config, filesystem):
    """Return a function for generating Template instances"""
    # doing it this way lets us pass params into the fixture
    def _template(name='test_template', content='# Simple Template'):
        template_path = filesystem.get_templates_base_path()
        template_path.mkdir(parents=True, exist_ok=True)
        (template_path / (name + '.md')).write_text(content)
        return Template(config, filesystem, name)
    return _template
