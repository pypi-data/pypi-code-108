import requests

from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new realnet group')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the group")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.name:
            call_args['name'] = args.name

        response = requests.post(self.get_url() + '/groups', headers=headers, json=call_args)
        print(response.json())

class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list available realnet groups')

    def add_arguments(self, parser):
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/groups', headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Name', 'Id']
            of.rows = [Extractor('name'), Extractor('id')]
            print(Out.format(response.json(), of))

class Delete(ProtoCmd, Client):

    def __init__(self):
        super().__init__('delete',
                         'delete a realnet group')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the group to be deleted")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.delete(self.get_url() + '/groups/{}'.format(args.id), headers=headers)
        print(response.json())

class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get a realnet group')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the group to be retrieved")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/groups/{}'.format(args.id), headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Property', 'Value']
            print(Out.format(response.json(), of))

class Update(ProtoCmd, Client):

    def __init__(self):
        super().__init__('update',
                         'update a realnet group')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the group")
        parser.add_argument('name', help="specifies the name of the group")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        call_args['name'] = args.name

        response = requests.put(self.get_url() + '/groups/{}'.format(args.id), headers=headers, json=call_args)
        print(response.json())

class AccountList(ProtoCmd, Client):

    def __init__(self):
        super().__init__('accounts',
                         'list accounts belonging to this realnet group')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the group")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/groups/{}/accounts'.format(args.id), headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Name', 'Id']
            of.rows = [Extractor('name'), Extractor('id')]
            print(Out.format(response.json(), of))

class AccountAdd(ProtoCmd, Client):

    def __init__(self):
        super().__init__('add',
                         'add an account to a realnet group')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the group")
        parser.add_argument('username', help="specifies the username of the account to be added to the group")
        parser.add_argument('role', help="specifies the role (root, admin, contributor, member or guest) of the account to be added to the group")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        call_args['username'] = args.username
        call_args['role'] = args.role

        response = requests.post(self.get_url() + '/groups/{}/accounts'.format(args.id), headers=headers, json=call_args)
        print(response.json())

class AccountRemove(ProtoCmd, Client):

    def __init__(self):
        super().__init__('remove',
                         'remove an account from a realnet group')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the group")
        parser.add_argument('account_id', help="specifies the id of the account to be removed from the group")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.delete(self.get_url() + '/groups/{}/accounts/{}'.format(args.id, args.account_id), headers=headers)
        print(response.json())

class Group(Shell):

        def __init__(self):
            super().__init__('group')

        def get_commands(self):
            return [
                List(),
                Create(),
                Delete(),
                Get(),
                Update(),
                AccountList(),
                AccountAdd(),
                AccountRemove()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Group shell'