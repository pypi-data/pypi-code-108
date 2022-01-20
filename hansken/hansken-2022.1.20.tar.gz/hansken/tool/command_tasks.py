# encoding=utf-8

from datetime import datetime

from iso8601 import parse_date
from logbook import Logger
from tabulate import tabulate, tabulate_formats

from hansken.remote import Connection
from hansken.tool import add_command
from hansken.util import omit_empty


log = Logger(__name__)


RELEVANT_DATES = {
    'queued': 'queuedOn',
    'running': 'startedOn',
    'cancelled': 'endedOn',
    'failed': 'endedOn',
    'completed': 'endedOn',
}


def filter_tasks(items, **filters):
    def item_matches(item):
        position, task = item
        # task matches if there's no filters provided or all of them match
        return not filters or all(task.get(key) == value for key, value in filters.items())

    yield from filter(item_matches, items)


def format_task(position, task):
    # select relevant values from the task
    return (
        position,
        task.get('id'),
        task.get('type'),
        task.get('targetProject'),
        task.get('status'),
        # determine relevant value for "since" by status
        task.get(RELEVANT_DATES.get(task.get('status'))),
    )


def render_tasks(tasks, tablefmt='simple', **filters):
    # pull relevant information from response (position on the queue (if present) and the task itself)
    tasks = ((item.get('queuePosition'), item.get('task')) for item in tasks)
    # prepare a 6-column table
    headers = ('position', 'id', 'type', 'project', 'status', 'since')
    tasks = [format_task(position, task) for position, task in filter_tasks(tasks, **filters)]
    # sort tabular data by position and the "since" column
    tasks = sorted(tasks, key=lambda row: (row[0] if row[0] is not None else -1, row[-1]))
    return tabulate(tasks, headers=headers, tablefmt=tablefmt)


def run_tasks_command(args):
    if not args.endpoint:
        tasks_parser.error('the following argument is required: ENDPOINT')

    if args.start and not args.end:
        args.end = datetime.now(tz=args.timezone)
        log.info('defaulting end of tasks range to {}', args.end)

    with Connection(args.endpoint, auth=args.auth, verify=args.verify) as connection:
        kwargs = omit_empty({
            'state': args.state,
            'project_id': args.project,
            'start': args.start,
            'end': args.end,
        })
        log.info('using {} selectors on tasks to be listed ({})', len(kwargs), set(kwargs.keys()))

        filters = omit_empty({
            'status': args.status,
        })
        log.info('applying {} filters on tasks to be listed ({})', len(filters), set(filters.keys()))

        # select tasks from remote by kwargs, apply filters locally
        print(render_tasks(connection.tasks(**kwargs), tablefmt=args.format, **filters))


tasks_parser = add_command('tasks', run_tasks_command, optional_project=True,
                           help='list either open or closed tasks tracked by the Hansken scheduler')

tasks_parser.add_argument('--state', metavar='STATE', choices=('open', 'closed'), default='open',
                          help='select state of tasks to list, one of {} (defaults to open)'
                               ''.format(', '.join(('open', 'closed'))))
tasks_parser.add_argument('--status', metavar='STATUS',
                          help='status of the tasks to list, e.g. queued or running')
tasks_parser.add_argument('--from', dest='start', type=parse_date,
                          help='minimum relevant date (optional time) tasks to list, in ISO 8601 format')
tasks_parser.add_argument('--to', dest='end', type=parse_date,
                          help='maximum relevant date (optional time) tasks to list, in ISO 8601 format '
                               '(automatically set to now if omitted)')
tasks_parser.add_argument('-f', '--format', metavar='FORMAT', choices=tabulate_formats, default='simple',
                          help='specify tabulation format, one of {} (see documentation of python module tabulate)'
                               ''.format(', '.join(tabulate_formats)))
