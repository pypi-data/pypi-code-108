import pytest
from pathlib import Path

from giwaxs_gui import App

__all__ = ['tested_app']


@pytest.fixture(scope='session', autouse=True)
def project_config_folder(tmpdir_factory):
    """Creates temporary directory for global app config"""
    return tmpdir_factory.mkdir('config')


@pytest.fixture(scope='session', autouse=True)
def tested_app(tmpdir_factory):
    config_dir = tmpdir_factory.mktemp('config')
    config_path: Path = Path(config_dir.strpath)
    App(config_path)
    yield
    for p in config_path.glob('*'):
        p.unlink()
    config_dir.remove()
