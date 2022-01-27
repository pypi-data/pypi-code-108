from mindsync.api import Api, purge, DEFAULT_BASE_URL
from mindsync.exc import MindsyncCliError
from mindsync.cli_handler import CliHandler

import os
import argparse
import logging
import json
import sys


def parse_command_line(cli_handler, args=sys.argv[1:]):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', help='Shows help message', action='store_true')
    parser.add_argument('--api-key', default=os.environ.get('MINDSYNC_API_KEY', None),
                        help='Api key can be found within mindsync profile. '
                        'If not specified an attempt to use MINDSYNC_API_KEY variable will be performed')
    parser.add_argument('--base-url', default=os.environ.get('MINDSYNC_BASE_URL', DEFAULT_BASE_URL),
                        help='Mindsync API base url. If not specified an attempt to use MINDSYNC_BASE_URL variable will be performed '
                             f'(default: {DEFAULT_BASE_URL})')
    parser.add_argument('--prettify', action='store_true', help='Prettify json output (default: %(default)s)')
    parser.add_argument('--meta', action='store_true', help='Include server response metadata to the output (default: %(default)s)')
    parser.add_argument('--log-level', default='INFO', help='Logging level from standard python logging module (default: %(default)s)')
    sp = parser.add_subparsers(title='subcommands', help='Use these subcommands to interact with the Mindsync platform')
    # profile
    profile_parser = sp.add_parser('profile', help='Mindsync platform profile related actions. By default returns user profile.')
    profile_parser.set_defaults(handler=cli_handler.profile)
    profile_parser.add_argument('--id', default=None, help='User id to get profile for')
    profile_sp = profile_parser.add_subparsers(title='profile subcommands', help='Profile related subcommands')
    # profile/set
    profile_set_parser = profile_sp.add_parser('set', help='Sets profile properties.')
    profile_set_parser.set_defaults(handler=cli_handler.set_profile)
    profile_set_parser.add_argument('--first-name', help='Set profile\'s first name')
    profile_set_parser.add_argument('--last-name', help='Set profile\'s last name')
    profile_set_parser.add_argument('--phone', help='Set profile\'s phone number')
    profile_set_parser.add_argument('--gravatar', help='Set profile\'s gravatar')
    profile_set_parser.add_argument('--nickname', help='Set profile\'s nickname')
    profile_set_parser.add_argument('--wallet_symbol', help='Set profile\'s wallet_symbol')
    profile_set_parser.add_argument('--wallet_address', help='Set profile\'s wallet_address')
    profile_set_parser.add_argument('--country', help='Set profile\'s country')
    profile_set_parser.add_argument('--city', help='Set profile\'s city')
    # rig
    rig_parser = sp.add_parser('rig', help='Mindsync platform rigs related actions. By default return all the rigs list.')
    rig_sp = rig_parser.add_subparsers(title='rigs subcommands', help='Rigs related subcommands')
    # rig/list
    rig_list_parser = rig_sp.add_parser('list', help='Returns all rigs list across the platform by default')
    rig_list_parser.set_defaults(handler=cli_handler.rigs_list)
    rig_list_parser.add_argument('--my', action='store_true', help='Filter list to only my rigs')
    # rig/info
    rig_info_parser = rig_sp.add_parser('info', help='Returns the rig info.')
    rig_info_parser.set_defaults(handler=cli_handler.rig_info)
    rig_info_parser.add_argument('--id', default=None, required=True, help='Rig id to get info of')
    # rig/set
    rig_info_set_parser = rig_sp.add_parser('set', help='Sets account properties.')
    rig_info_set_parser.set_defaults(handler=cli_handler.set_rig, enable=None)
    rig_info_set_parser.add_argument('--id', default=None, required=True, help='Rig id to get info of')
    rig_info_set_parser.add_argument('--enable', dest='enable', action='store_true', help='Enables rig')
    rig_info_set_parser.add_argument('--disable', dest='enable', action='store_false', help='Disables rig')
    rig_info_set_parser.add_argument('--power-cost', type=float, help='Sets the power cost')
    # rig/tariffs
    rig_info_set_parser = rig_sp.add_parser('tariffs', help='Get tariffs.')
    rig_info_set_parser.set_defaults(handler=cli_handler.rig_tariffs)
    rig_info_set_parser.add_argument('--id', default=None, help='Rig id to get tariffs of')
    # rent
    rent_parser = sp.add_parser('rent', help='Mindsync platform rents related actions. By default returns...')
    rent_sp = rent_parser.add_subparsers(title='rent subcommands', help='Rent related subcommands')
    # rent/list
    rent_list_parser = rent_sp.add_parser('list', help='Returns all active rents list across the platform')
    rent_list_parser.set_defaults(handler=cli_handler.rents_list)
    rent_list_parser.add_argument('--my', action='store_true', help='Filter list to only my rents')
    # rent/start
    rent_start_parser = rent_sp.add_parser('start', help='Starts rent')
    rent_start_parser.set_defaults(handler=cli_handler.start_rent)
    rent_start_parser.add_argument('--id', required=True, help='Rig id to rent')
    rent_start_parser.add_argument('--tariff', required=True, choices=['demo', 'dynamic', 'fixed'], help='Tarrif to use')
    # rent/stop
    rent_stop_parser = rent_sp.add_parser('stop', help='Stops rent certain rent')
    rent_stop_parser.set_defaults(handler=cli_handler.stop_rent)
    rent_stop_parser.add_argument('--id', required=True, help='Rent id to stop in uuid format')
    # rent/state
    rent_state_parser = rent_sp.add_parser('state', help='Returns rent state')
    rent_state_parser.set_defaults(handler=cli_handler.rent_state)
    rent_state_parser.add_argument('--id', required=True, help='Rent id to retrieve state for in uuid format')
    # rent/info
    rent_info_parser = rent_sp.add_parser('info', help='Returns rent info')
    rent_info_parser.set_defaults(handler=cli_handler.rent_info)
    rent_info_parser.add_argument('--id', required=True, help='Rent id to retrieve info for')
    # rent/set
    rent_set_parser = rent_sp.add_parser('set', help='Sets rent parameters')
    rent_set_parser.set_defaults(handler=cli_handler.set_rent)
    rent_set_parser.add_argument('--id', required=True, help='Rent id to retrieve info for')
    rent_set_parser.add_argument('--enable', dest='enable', action='store_true', help='Enables rent')
    rent_set_parser.add_argument('--disable', dest='enable', action='store_false', help='Disables rent')
    rent_set_parser.add_argument('--login', help='Protect rent with login/password')
    rent_set_parser.add_argument('--password', help='Protect rent with login/password')

    args = parser.parse_args(args)
    effective_args = purge(vars(args))

    del effective_args['help']
    if not effective_args:
        return None, parser

    return args, parser


def main():
    try:
        _main()
    except SystemExit:
        raise
    except MindsyncCliError as e:
        print(e.args[0], file=sys.stderr)
        e.args[1].print_help()


def _main():
    cli_handler = CliHandler()
    args, parser = parse_command_line(cli_handler)
    logging.basicConfig(level=args.log_level)
    logging.debug(f'CLI Args: [{args}]')

    if args is not None and args.help:
        parser.print_help()
        return

    if args is None or not hasattr(args, 'handler'):
        raise MindsyncCliError('No command specified', parser)

    if args.api_key is None:
        raise MindsyncCliError('No API key defined', parser)

    api = Api(args.api_key, args.base_url)
    cli_handler.bind(api)
    dict_args = vars(args)
    if not args.meta:
        dict_args.pop('meta', None)

    rv = args.handler(**dict_args)
    _print(rv, args)


def _print(rv, args):
    if args.prettify:
        print(json.dumps(rv, indent=4, sort_keys=True))
    else:
        print(json.dumps(rv))
