import requests

from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new realnet tenant')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the tenant")
        parser.add_argument('--username', help="specifies the username of the tenant root account")
        parser.add_argument('--password', help="specifies the password for the tenant root account")
        parser.add_argument('--email', help="specifies the email for the tenant root account")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        call_args['name'] = args.name

        if args.username:
            call_args['username'] = args.username

        if args.password:
            call_args['password'] = args.password

        if args.email:
            call_args['email'] = args.email

        response = requests.post(self.get_url() + '/tenants', headers=headers, json=call_args)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Property', 'Value']
            print(Out.format(response.json(), of))

class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list available realnet tenants')

    def add_arguments(self, parser):
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/tenants', headers=headers)

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
                         'delete a realnet tenant')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the tenant to be deleted")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.delete(self.get_url() + '/tenants/{}'.format(args.name), headers=headers)
        print(response.json())

class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get a realnet tenant')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the tenant to be retrieved")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/tenants/{}'.format(args.name), headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Property', 'Value']
            print(Out.format(response.json(), of))

class Update(ProtoCmd, Client):

    def __init__(self):
        super().__init__('update',
                         'update a realnet tenant')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the tenant")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        # call_args['name'] = args.name

        response = requests.put(self.get_url() + '/tenants/{}'.format(args.name), headers=headers, json=call_args)
        print(response.json())


class Tenant(Shell):

        def __init__(self):
            super().__init__('tenant')

        def get_commands(self):
            return [
                List(),
                Create(),
                Delete(),
                Get(),
                Update(),
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Tenant shell'