from las import Client

from lascli.util import NotProvided, nullable


def get_organization(las_client: Client, organization_id):
    return las_client.get_organization(organization_id)


def update_organization(
    las_client: Client,
    organization_id,
    **optional_args,
):
    return las_client.update_organization(organization_id=organization_id, **optional_args)


def create_organizations_parser(subparsers):
    parser = subparsers.add_parser('organizations')
    subparsers = parser.add_subparsers()

    get_parser = subparsers.add_parser('get')
    get_parser.add_argument('organization_id')
    get_parser.set_defaults(cmd=get_organization)

    update_parser = subparsers.add_parser('update')
    update_parser.add_argument('organization_id')
    update_parser.add_argument('--name', type=nullable, default=NotProvided)
    update_parser.add_argument('--description', type=nullable, default=NotProvided)
    update_parser.set_defaults(cmd=update_organization)

    return parser
