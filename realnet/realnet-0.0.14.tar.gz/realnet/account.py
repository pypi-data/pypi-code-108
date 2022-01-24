import requests

from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new realnet account')

    def add_arguments(self, parser):
        parser.add_argument('type', help="specifies the type for the account (person or thing)")
        parser.add_argument('role', help="specifies the role for the account (root, admin, contributor, member or guest)")
        parser.add_argument('username', help="specifies the username of the account")
        parser.add_argument('password', help="specifies the password for the account")
        parser.add_argument('email', help="specifies the email for the account")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        call_args['username'] = args.username
        call_args['password'] = args.password
        call_args['role'] = args.role
        call_args['type'] = args.type
        call_args['email'] = args.email

        response = requests.post(self.get_url() + '/accounts', headers=headers, json=call_args)
        print(response.json())

class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list available realnet accounts')

    def add_arguments(self, parser):
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/accounts', headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Username', 'Id']
            of.rows = [Extractor('username'), Extractor('id')]
            print(Out.format(response.json(), of))

class Delete(ProtoCmd, Client):

    def __init__(self):
        super().__init__('delete',
                         'delete a realnet account')

    def add_arguments(self, parser):
        parser.add_argument('username', help="specifies the username of the account to be deleted")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.delete(self.get_url() + '/accounts/{}'.format(args.username), headers=headers)
        print(response.json())

class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get a realnet account')

    def add_arguments(self, parser):
        parser.add_argument('username', help="specifies the username of the account to be retrieved")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/accounts/{}'.format(args.username), headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Property', 'Value']
            print(Out.format(response.json(), of))

class Update(ProtoCmd, Client):

    def __init__(self):
        super().__init__('update',
                         'update a realnet account')

    def add_arguments(self, parser):
        parser.add_argument('username', help="specifies the username of the account")
        parser.add_argument('--password', help="specifies the new password for the account")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if 'password' in args:
            call_args['password'] = args.password

        response = requests.put(self.get_url() + '/accounts/{}'.format(args.username), headers=headers, json=call_args)
        print(response.json())


class Account(Shell):

        def __init__(self):
            super().__init__('account')

        def get_commands(self):
            return [
                List(),
                Create(),
                Delete(),
                Get(),
                Update()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Account shell'