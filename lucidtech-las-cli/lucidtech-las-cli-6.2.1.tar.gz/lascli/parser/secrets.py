import json
import pathlib

from las import Client

from lascli.util import nullable, NotProvided


def _create_secret_dict(secret_data, secret_path):
    data = None

    if secret_data:
        data = {}
        for data_entry in secret_data:
            key, val = data_entry.split('=', 1)
            data[key] = val

    if secret_path:
        data = json.loads(pathlib.Path(secret_path).read_text())

    return data


def list_secrets(las_client: Client, max_results, next_token):
    return las_client.list_secrets(max_results=max_results, next_token=next_token)


def create_secret(las_client: Client, secret_data, secret_path, **optional_args):
    data = _create_secret_dict(secret_data, secret_path)
    return las_client.create_secret(data, **optional_args)


def update_secret(las_client: Client, secret_id, secret_data, secret_path, **optional_args):
    data = _create_secret_dict(secret_data, secret_path)
    return las_client.update_secret(secret_id, data=data, **optional_args)


def delete_secret(las_client: Client, secret_id):
    return las_client.delete_secret(secret_id)


def create_secrets_parser(subparsers):
    parser = subparsers.add_parser('secrets')
    subparsers = parser.add_subparsers()

    list_secrets_parser = subparsers.add_parser('list')
    list_secrets_parser.add_argument('--max-results', '-m', type=int, default=None)
    list_secrets_parser.add_argument('--next-token', '-n', type=str, default=None)
    list_secrets_parser.set_defaults(cmd=list_secrets)

    create_secret_parser = subparsers.add_parser('create')
    create_secret_value_group = create_secret_parser.add_mutually_exclusive_group(required=True)
    create_secret_value_group.add_argument('--secret-data', metavar='KEY=VALUE', nargs='+')
    create_secret_value_group.add_argument('--secret-path', type=str, help='Path to JSON file')
    create_secret_parser.add_argument('--name')
    create_secret_parser.add_argument('--description')
    create_secret_parser.set_defaults(cmd=create_secret)

    update_secret_parser = subparsers.add_parser('update')
    update_secret_parser.add_argument('secret_id')
    update_secret_value_group = update_secret_parser.add_mutually_exclusive_group(required=False)
    update_secret_value_group.add_argument('--secret-data', metavar='KEY=VALUE', nargs='+')
    update_secret_value_group.add_argument('--secret-path', type=str, help='Path to JSON file')
    update_secret_parser.add_argument('--name', type=nullable, default=NotProvided)
    update_secret_parser.add_argument('--description', type=nullable, default=NotProvided)
    update_secret_parser.set_defaults(cmd=update_secret)

    delete_secret_parser = subparsers.add_parser('delete')
    delete_secret_parser.add_argument('secret_id')
    delete_secret_parser.set_defaults(cmd=delete_secret)

    return parser
