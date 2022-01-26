import json
import pathlib

from las import Client

from lascli.util import nullable, NotProvided


def create_transition(
    las_client: Client,
    transition_type,
    in_schema_path=None,
    out_schema_path=None,
    parameters_path=None,
    **optional_args,
):
    in_schema = json.loads(pathlib.Path(in_schema_path).read_text()) if in_schema_path else None
    out_schema = json.loads(pathlib.Path(out_schema_path).read_text()) if out_schema_path else None
    parameters = json.loads(pathlib.Path(parameters_path).read_text()) if parameters_path else None
    return las_client.create_transition(
        transition_type,
        in_schema=in_schema,
        out_schema=out_schema,
        parameters=parameters,
        **optional_args
    )


def list_transitions(las_client: Client, **optional_args):
    return las_client.list_transitions(**optional_args)


def get_transition(las_client: Client, transition_id):
    return las_client.get_transition(transition_id)


def update_transition(
    las_client: Client,
    transition_id,
    in_schema_path=None,
    out_schema_path=None,
    assets_path=None,
    environment_path=None,
    environment_secrets=None,
    **optional_args,
):
    in_schema = json.loads(pathlib.Path(in_schema_path).read_text()) if in_schema_path else None
    out_schema = json.loads(pathlib.Path(out_schema_path).read_text()) if out_schema_path else None
    assets = json.loads(pathlib.Path(assets_path).read_text()) if assets_path else None
    environment = json.loads(pathlib.Path(environment_path).read_text()) if environment_path else None
    return las_client.update_transition(
        transition_id,
        in_schema=in_schema,
        out_schema=out_schema,
        assets=assets,
        environment=environment,
        environment_secrets=environment_secrets,
        **optional_args,
    )


def execute_transition(las_client: Client, transition_id):
    return las_client.execute_transition(transition_id)


def delete_transition(las_client: Client, transition_id):
    return las_client.delete_transition(transition_id)


def list_transition_executions(las_client: Client, transition_id, **optional_args):
    return las_client.list_transition_executions(transition_id, **optional_args)


def get_transition_execution(las_client: Client, transition_id, execution_id):
    return las_client.get_transition_execution(transition_id, execution_id)


def update_transition_execution(
    las_client: Client,
    transition_id,
    execution_id,
    status,
    error_path=None,
    output_path=None,
    start_time=None,
):
    output_dict = json.loads(pathlib.Path(output_path).read_text()) if output_path else None
    error_dict = json.loads(pathlib.Path(error_path).read_text()) if error_path else None
    return las_client.update_transition_execution(
        transition_id,
        execution_id,
        status,
        output=output_dict,
        error=error_dict,
        start_time=start_time,
    )


def send_heartbeat(las_client: Client, transition_id, execution_id):
    return las_client.send_heartbeat(transition_id, execution_id)


def create_transitions_parser(subparsers):
    parser = subparsers.add_parser('transitions')
    subparsers = parser.add_subparsers()

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('transition_type', choices=["docker", "manual"])
    create_parser.add_argument('--parameters-path', '-p', help='parameters to the docker image')
    create_parser.add_argument('--in-schema-path')
    create_parser.add_argument('--out-schema-path')
    create_parser.add_argument('--name')
    create_parser.add_argument('--description')
    create_parser.set_defaults(cmd=create_transition)

    list_parser = subparsers.add_parser('list')
    list_parser.add_argument('--transition-type', '-t', nargs='+')
    list_parser.add_argument('--max-results', '-m', type=int)
    list_parser.add_argument('--next-token', '-n', type=str)
    list_parser.set_defaults(cmd=list_transitions)

    get_parser = subparsers.add_parser('get')
    get_parser.add_argument('transition_id')
    get_parser.set_defaults(cmd=get_transition)

    update_parser = subparsers.add_parser('update')
    update_parser.add_argument('transition_id')
    update_parser.add_argument('--name', type=nullable, default=NotProvided)
    update_parser.add_argument('--in-schema-path')
    update_parser.add_argument('--out-schema-path')
    update_parser.add_argument(
        '--assets-path',
        help='Path to json file with str keys and values that are assetIds, only possible for a manual transition'
    )
    update_parser.add_argument(
        '--environment-path',
        help='Path to json file with environment variables, only possible for a docker transition',
    )
    update_parser.add_argument(
        '--environment-secrets',
        nargs='+',
        help='secretIds that that will be used as environment variables, only possible for a docker transition',
    )
    update_parser.add_argument('--description', type=nullable, default=NotProvided)
    update_parser.set_defaults(cmd=update_transition)

    execute_parser = subparsers.add_parser('execute')
    execute_parser.add_argument('transition_id')
    execute_parser.set_defaults(cmd=execute_transition)

    delete_parser = subparsers.add_parser(
        'delete',
        description='Will fail if transition is in use by one or more workflows',
    )
    delete_parser.add_argument('transition_id')
    delete_parser.set_defaults(cmd=delete_transition)

    list_executions_parser = subparsers.add_parser('list-executions')
    list_executions_parser.add_argument('transition_id')
    list_executions_parser.add_argument('--execution-id', nargs='+', help='Perform a batch-get on the ids')
    list_executions_parser.add_argument('--status', '-s', nargs='+', help='Only return those with the given status')
    list_executions_parser.add_argument('--order')
    list_executions_parser.add_argument('--sort-by')
    list_executions_parser.add_argument('--max-results', '-m', type=int)
    list_executions_parser.add_argument('--next-token', '-n', type=str)
    list_executions_parser.set_defaults(cmd=list_transition_executions)

    get_execution_parser = subparsers.add_parser('get-execution')
    get_execution_parser.add_argument('transition_id')
    get_execution_parser.add_argument('execution_id')
    get_execution_parser.set_defaults(cmd=get_transition_execution)

    update_execution_parser = subparsers.add_parser('update-execution')
    update_execution_parser.add_argument('transition_id')
    update_execution_parser.add_argument('execution_id')
    update_execution_parser.add_argument('status', choices=['succeeded', 'failed', 'rejected', 'retry'])
    update_execution_parser.add_argument('--output_path', '-o')
    update_execution_parser.add_argument('--error_path', '-e')
    update_execution_parser.add_argument('--start-time')
    update_execution_parser.set_defaults(cmd=update_transition_execution)

    send_heartbeat_parser = subparsers.add_parser('heartbeat')
    send_heartbeat_parser.add_argument('transition_id')
    send_heartbeat_parser.add_argument('execution_id')
    send_heartbeat_parser.set_defaults(cmd=send_heartbeat)

    return parser
