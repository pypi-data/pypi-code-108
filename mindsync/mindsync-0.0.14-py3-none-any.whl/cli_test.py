from mindsync.cli_handler import CliHandler
from mindsync.cli import parse_command_line
from mindsync.api import DEFAULT_BASE_URL

from argparse import Namespace

import pytest
from unittest.mock import create_autospec


API_KEY = 'does-not-matter'
BASE_URL = 'https://whatever'
RIG_ID = 'a-rig-id'
PROFILE_ID = 'a-profile-id'
RENT_ID = 'a-rent-id'

@pytest.fixture
def cli_handler_mock():
    return create_autospec(CliHandler, spec_set=True)


@pytest.fixture
def api_key():
    return API_KEY


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.mark.parametrize('args, expected_args', [(['--api-key', API_KEY, '--log-level', 'DEBUG', '--base-url', BASE_URL, 'rig', 'list'], 
                                                 Namespace(help=False, log_level='DEBUG', prettify=False, my=False, handler='rigs_list', api_key=API_KEY, base_url=BASE_URL)),
                                                 (['--api-key', API_KEY, 'rig', 'list'], 
                                                 Namespace(help=False, log_level='INFO',  prettify=False, my=False, handler='rigs_list', api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rig', 'list', '--my'], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, my=True, handler='rigs_list', api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, '--prettify', 'rig', 'list', '--my'], 
                                                 Namespace(help=False, log_level='INFO', prettify=True, my=True, handler='rigs_list', api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rig', 'info', '--id', RIG_ID], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, handler='rig_info', id=RIG_ID, api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rig', 'set', '--id', RIG_ID, '--enable'], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, handler='set_rig', enable=True, power_cost=None, id=RIG_ID, api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rig', 'set', '--id', RIG_ID, '--disable'], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, handler='set_rig', enable=False, power_cost=None, id=RIG_ID, api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rig', 'set', '--id', RIG_ID, '--enable', '--power-cost', '0.25'], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, handler='set_rig', enable=True, power_cost=0.25, id=RIG_ID, api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'profile'], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, handler='profile', id=None, api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'profile', '--id', PROFILE_ID], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, handler='profile', id=PROFILE_ID, api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'profile', 'set', '--first-name', "Someone's name"], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, handler='set_profile', api_key=API_KEY, base_url=DEFAULT_BASE_URL, 
                                                          first_name="Someone's name", last_name=None, phone=None, gravatar=None, nickname=None, 
                                                          wallet_symbol=None, wallet_address=None, country=None, city=None, id=None)), 
                                                 (['--api-key', API_KEY, 'rig', 'tariffs'], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, handler='rig_tariffs', id=None, api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rig', 'tariffs', '--id', RIG_ID], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, handler='rig_tariffs', id=RIG_ID, api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rent', 'list'], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, my=False, handler='rents_list', api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rent', 'list', '--my'], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, my=True, handler='rents_list', api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rent', 'start', '--id', RIG_ID, '--tariff', 'demo'], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, id=RIG_ID, tariff='demo', handler='start_rent', api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rent', 'stop', '--id', RIG_ID], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, id=RIG_ID, handler='stop_rent', api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rent', 'state', '--id', RIG_ID], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, id=RIG_ID, handler='rent_state', api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rent', 'info', '--id', RIG_ID], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, id=RIG_ID, handler='rent_info', api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                 (['--api-key', API_KEY, 'rent', 'set', '--id', RENT_ID, '--enable', '--login', 'user', '--password', 'password'], 
                                                 Namespace(help=False, log_level='INFO', prettify=False, handler='set_rent', enable=True, login='user', password='password', id=RENT_ID, api_key=API_KEY, base_url=DEFAULT_BASE_URL)), 
                                                ])
def test_parse_command_line_must_setup_right_command_handler(cli_handler_mock, args, expected_args):
    args, _ = parse_command_line(cli_handler_mock, args=args)
    print(args)
    assert args.handler
    args.handler(args)

    method_name = expected_args.handler
    expected_args.handler = getattr(cli_handler_mock, method_name)
    called_method = getattr(cli_handler_mock, method_name)
    called_method.assert_called_with(expected_args)
