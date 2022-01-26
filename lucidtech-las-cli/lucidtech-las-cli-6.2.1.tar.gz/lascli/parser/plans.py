from las import Client


def list_plans(las_client: Client, owner, max_results, next_token):
    return las_client.list_plans(owner=owner, max_results=max_results, next_token=next_token)


def get_plan(las_client: Client, plan_id):
    return las_client.get_plan(plan_id)


def create_plans_parser(subparsers):
    parser = subparsers.add_parser('plans')
    subparsers = parser.add_subparsers()

    list_plans_parser = subparsers.add_parser('list')
    list_plans_parser.add_argument('--owner', '-o', nargs='+', help='Organizations whose plans to list')
    list_plans_parser.add_argument('--max-results', '-m', type=int, default=None)
    list_plans_parser.add_argument('--next-token', '-n', type=str, default=None)
    list_plans_parser.set_defaults(cmd=list_plans)

    get_plan_parser = subparsers.add_parser('get')
    get_plan_parser.add_argument('plan_id')
    get_plan_parser.set_defaults(cmd=get_plan)

    return parser
