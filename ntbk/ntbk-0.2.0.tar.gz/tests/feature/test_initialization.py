"""Tests for application initialization"""

import ntbk.initialize
from ntbk.config import Config

# TODO - need to test dispatching a normal command and making sure the init procedures run

def test_initializing_config_file(tmp_path, mocker):
    """Test inititializing the app config file"""
    # mock the user input prompts - return ~/ntbk for the first prompt, and vim for the second
    mocker.patch('builtins.input', side_effect=['~/ntbk', 'vim'])
    config_file = tmp_path / 'ntbk.yml'
    conf = Config(file_path=config_file)
    ntbk.initialize.init_config_file(conf)
    assert config_file.exists()
    assert conf.get('ntbk_dir') == '~/ntbk'
    assert conf.get('editor') == 'vim'

def test_initializing_notebook(tmp_path):
    """Test inititializing a new notebook"""
    ntbk_dir = tmp_path / 'ntbk' # dir does not exist yet
    conf = Config({'ntbk_dir': str(ntbk_dir)})
    expected_dirs = ['collections', 'log', '_templates']
    assert not ntbk_dir.exists()
    ntbk.initialize.init_notebook(conf)
    assert ntbk_dir.exists()
    for expected_dir in expected_dirs:
        assert (ntbk_dir / expected_dir).exists()
