import base64
import logging
import pathlib

from las import Client

from lascli.util import nullable, NotProvided


def get_asset(las_client: Client, asset_id, download_content, output_content):
    asset_resp = las_client.get_asset(asset_id)
    content = asset_resp['content']

    if download_content:
        logging.info(f'Downloading content to {download_content}')
        binary = base64.b64decode(content)
        pathlib.Path(download_content).write_bytes(binary)

    if output_content:
        return asset_resp
    else:
        return {**asset_resp, 'content': asset_resp['content'][:10] + '... [TRUNCATED]'}


def list_assets(las_client: Client, max_results=None, next_token=None):
    return las_client.list_assets(max_results=max_results, next_token=next_token)


def create_asset(las_client: Client, asset_path, **optional_args):
    content = pathlib.Path(asset_path).read_bytes()
    return las_client.create_asset(content, **optional_args)


def update_asset(las_client: Client, asset_id, asset_path=None, **optional_args):
    if asset_path:
        optional_args['content'] = pathlib.Path(asset_path).read_bytes()

    return las_client.update_asset(asset_id, **optional_args)


def delete_asset(las_client: Client, asset_id):
    return las_client.delete_asset(asset_id)


def create_assets_parser(subparsers):
    parser = subparsers.add_parser('assets')
    subparsers = parser.add_subparsers()

    get_asset_parser = subparsers.add_parser('get')
    get_asset_parser.add_argument('asset_id')
    get_asset_parser.add_argument('--output-content', action='store_true')
    get_asset_parser.add_argument('-d', '--download-content')
    get_asset_parser.set_defaults(cmd=get_asset)

    list_assets_parser = subparsers.add_parser('list')
    list_assets_parser.add_argument('--max-results', '-m', type=int, default=None)
    list_assets_parser.add_argument('--next-token', '-n', default=None)
    list_assets_parser.set_defaults(cmd=list_assets)

    create_asset_parser = subparsers.add_parser('create')
    create_asset_parser.add_argument('asset_path')
    create_asset_parser.add_argument('--name')
    create_asset_parser.add_argument('--description')
    create_asset_parser.set_defaults(cmd=create_asset)

    update_asset_parser = subparsers.add_parser('update')
    update_asset_parser.add_argument('asset_id')
    update_asset_parser.add_argument('--asset-path')
    update_asset_parser.add_argument('--name', type=nullable, default=NotProvided)
    update_asset_parser.add_argument('--description', type=nullable, default=NotProvided)
    update_asset_parser.set_defaults(cmd=update_asset)

    delete_asset_parser = subparsers.add_parser('delete')
    delete_asset_parser.add_argument('asset_id')
    delete_asset_parser.set_defaults(cmd=delete_asset)

    return parser
