from datetime import datetime
from las import Client


def parse_log(response):
    log_events = []
    for event in response['events']:
        timestamp = event['timestamp']
        message = event['message']
        log_events.append(f'{datetime.fromtimestamp(timestamp)}: {message}')
    return '\n'.join(log_events)


def list_logs(
    las_client: Client,
    max_results,
    next_token,
    transition_id,
    transition_execution_id,
    workflow_id,
    workflow_execution_id,
):
    return las_client.list_logs(
        max_results=max_results,
        next_token=next_token,
        transition_id=transition_id,
        transition_execution_id=transition_execution_id,
        workflow_id=workflow_id,
        workflow_execution_id=workflow_execution_id,
    )


def get_log(las_client: Client, log_id, pretty):
    response = las_client.get_log(log_id)
    if pretty:
        response = parse_log(response)
    return response


def create_logs_parser(subparsers):
    parser = subparsers.add_parser('logs')
    subparsers = parser.add_subparsers()

    get_log_parser = subparsers.add_parser('get')
    get_log_parser.add_argument('log_id')
    get_log_parser.add_argument('--pretty', action='store_true', help='Parse output to make it more readable')
    get_log_parser.set_defaults(cmd=get_log)

    list_logs_parser = subparsers.add_parser('list')
    list_logs_parser.add_argument('--max-results', '-m', type=int, default=None)
    list_logs_parser.add_argument('--next-token', '-n', type=str, default=None)
    list_logs_parser.add_argument('--workflow-id')
    list_logs_parser.add_argument('--workflow-execution-id')
    list_logs_parser.add_argument('--transition-id')
    list_logs_parser.add_argument('--transition-execution-id')
    list_logs_parser.set_defaults(cmd=list_logs)
    return parser
