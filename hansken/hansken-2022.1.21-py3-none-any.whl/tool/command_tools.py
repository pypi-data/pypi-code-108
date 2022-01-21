# encoding=utf-8

import warnings

from logbook import Logger
from tabulate import tabulate, tabulate_formats

from hansken.remote import Connection
from hansken.tool import add_command


log = Logger(__name__)


def run_tools_command(args):
    if not args.endpoint:
        tools_parser.error('the following argument is required: ENDPOINT')

    with Connection(args.endpoint, auth=args.auth, verify=args.verify) as connection:
        table = connection.tools()
        # transform the returned data format into a matrix of 4-tuples
        table = [('[x]' if tool.get('defaultEnabled') else '[ ]',
                  name,
                  tool.get('version'),
                  tool.get('description'))
                 for name, tool in table.items()]

        # print the table, sorted by the name column
        print(tabulate(sorted(table, key=lambda tool: tool[1]),
                       headers=('', 'name', 'version', 'description'),
                       tablefmt=args.format))


def run_tools(*args, **kwargs):
    warnings.warn('{0}.run_tools has been renamed to {0}.run_tools_command'.format(__name__),
                  DeprecationWarning)
    run_tools_command(*args, **kwargs)


tools_parser = add_command('tools',
                           run_tools_command,
                           optional_project=False,
                           help='print a table of available extraction tools')
tools_parser.add_argument('-f', '--format', metavar='FORMAT', choices=tabulate_formats, default='simple',
                          help='specify tabulation format, one of {} (see documentation of python module tabulate)'
                               ''.format(', '.join(tabulate_formats)))
