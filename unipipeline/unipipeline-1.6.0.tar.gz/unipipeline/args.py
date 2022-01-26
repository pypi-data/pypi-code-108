import json
import os.path
from argparse import ArgumentParser, ArgumentTypeError
from typing import Union, Dict, Any

CWD = str(os.getcwdb())


def str2bool(v: Union[str, bool]) -> bool:
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    raise ArgumentTypeError('Boolean value expected.')


def file(v: str) -> str:
    if os.path.isfile(v):
        return v
    rel = str(os.path.join(CWD, os.path.normpath(v)))
    if os.path.isfile(rel):
        return rel
    raise ArgumentTypeError(f'file {v} is not exists')


def json_data(v: str) -> Dict[str, Any]:
    try:
        return json.loads(v)  # type: ignore
    except Exception as e:  # noqa
        raise ArgumentTypeError(f'INVALID JSON: {e}')


CMD_INIT = 'init'
CMD_CHECK = 'check'
CMD_CONSUME = 'consume'
CMD_PRODUCE = 'produce'
CMD_CRON = 'cron'
CMD_SCAFFOLD = 'scaffold'


parser = ArgumentParser(description='UNIPIPELINE: simple way to build the declarative and distributed data pipelines. this is cli tool for unipipeline')
parser.usage = 'unipipeline --help'

DEFAULT_CONFIG_FILE = './unipipeline.yml'
parser.add_argument('--config-file', '-f', default=DEFAULT_CONFIG_FILE, type=file, dest='config_file', help=f'path to unipipeline config file (default: {DEFAULT_CONFIG_FILE})', required=True)
parser.add_argument('--verbose', default=False, type=str2bool, const=True, nargs='?', dest='verbose', help='verbose output (default: false)')

subparsers = parser.add_subparsers(help='sub-commands', required=True, dest='cmd')

check_help = 'check loading of all modules'
check_parser = subparsers.add_parser(CMD_CHECK, help=check_help)
check_parser.description = check_help
check_parser.usage = f'''
    unipipeline -f {DEFAULT_CONFIG_FILE} {CMD_CHECK}
    unipipeline -f {DEFAULT_CONFIG_FILE} --verbose=yes {CMD_CHECK}
'''

scaffold_help = 'create all modules and classes if it is absent. no args'
scaffold_parser = subparsers.add_parser(CMD_SCAFFOLD, help=scaffold_help)
scaffold_parser.description = scaffold_help
scaffold_parser.usage = f'''
    unipipeline -f {DEFAULT_CONFIG_FILE} {CMD_SCAFFOLD}
    unipipeline -f {DEFAULT_CONFIG_FILE} --verbose=yes {CMD_SCAFFOLD}
'''

init_help = 'initialize broker topics for workers'
init_parser = subparsers.add_parser(CMD_INIT, help=init_help)
init_parser.add_argument('--workers', '-w', type=str, nargs='+', default=[], required=False, dest='init_workers', help='workers list for initialization (default: [])')
init_parser.description = init_help
init_parser.usage = f'''
    unipipeline -f {DEFAULT_CONFIG_FILE} {CMD_INIT}
    unipipeline -f {DEFAULT_CONFIG_FILE} --verbose=yes {CMD_INIT}
    unipipeline -f {DEFAULT_CONFIG_FILE} --verbose=yes {CMD_INIT} --workers some_worker_name_01 some_worker_name_02
'''

consume_help = 'start consuming workers. connect to brokers and waiting for messages'
consume_parser = subparsers.add_parser(CMD_CONSUME, help=consume_help)
consume_parser.add_argument('--workers', '-w', type=str, nargs='+', required=True, dest='consume_workers', help='worker list for consuming')
consume_parser.description = consume_help
consume_parser.usage = f'''
    unipipeline -f {DEFAULT_CONFIG_FILE} {CMD_CONSUME}
    unipipeline -f {DEFAULT_CONFIG_FILE} --verbose=yes {CMD_CONSUME}
    unipipeline -f {DEFAULT_CONFIG_FILE} {CMD_CONSUME} --workers some_worker_name_01 some_worker_name_02
    unipipeline -f {DEFAULT_CONFIG_FILE} --verbose=yes {CMD_CONSUME} --workers some_worker_name_01 some_worker_name_02
'''

cron_help = 'start cron jobs, That defined in config file'
cron_parser = subparsers.add_parser(CMD_CRON, help=cron_help)
cron_parser.description = cron_help
cron_parser.usage = f'''
    unipipeline -f {DEFAULT_CONFIG_FILE} {CMD_CRON}
    unipipeline -f {DEFAULT_CONFIG_FILE} --verbose=yes {CMD_CRON}
'''

produce_help = 'publish message to broker. send it to worker'
produce_parser = subparsers.add_parser(CMD_PRODUCE, help=produce_help)
produce_parser.add_argument('--alone', '-a', type=str2bool, nargs='?', const=True, default=False, dest='produce_alone', help='message will be sent only if topic is empty')
produce_parser.add_argument('--worker', '-w', type=str, required=True, dest='produce_worker', help='worker recipient')
produce_parser.add_argument('--data', '-d', type=json_data, required=True, dest='produce_data', help='data for sending')
produce_parser.description = produce_help
produce_parser.usage = f'''
    unipipeline -f {DEFAULT_CONFIG_FILE} {CMD_PRODUCE} --worker some_worker_name_01 --data {{"some": "json", "value": "for worker"}}
    unipipeline -f {DEFAULT_CONFIG_FILE} --verbose=yes {CMD_PRODUCE} --worker some_worker_name_01 --data {{"some": "json", "value": "for worker"}}
    unipipeline -f {DEFAULT_CONFIG_FILE} {CMD_PRODUCE} --alone --worker some_worker_name_01 --data {{"some": "json", "value": "for worker"}}
    unipipeline -f {DEFAULT_CONFIG_FILE} --verbose=yes {CMD_PRODUCE} --alone --worker some_worker_name_01 --data {{"some": "json", "value": "for worker"}}
'''


def parse_args() -> Any:
    return parser.parse_args()
