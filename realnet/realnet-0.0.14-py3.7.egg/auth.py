import requests

from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new realnet authenticator')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the authenticator")
        parser.add_argument('--api_base_url', help="specifies the api base url")
        parser.add_argument('--request_token_url', help="specifies the request token url")
        parser.add_argument('--access_token_url', help="specifies the access token url")
        parser.add_argument('--authorize_url', help="specifies the authorize url")
        parser.add_argument('--client_kwarg', action='append', help="specifies the client kwarg name:value")
        parser.add_argument('--userinfo_endpoint', help="specifies the userinfo endpoint")
        parser.add_argument('--client_id', help="specifies the client_id")
        parser.add_argument('--client_secret', help="specifies the client_id")
        parser.add_argument('--server_metadata_url', help="specifies the server metadata url")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.name:
            call_args['name'] = args.name

        if args.api_base_url:
            call_args['api_base_url'] = args.api_base_url

        if args.request_token_url:
            call_args['request_token_url'] = args.request_token_url

        if args.access_token_url:
            call_args['access_token_url'] = args.access_token_url

        if args.authorize_url:
            call_args['authorize_url'] = args.authorize_url

        if args.client_kwarg:
            data = dict()
            for att in args.client_kwarg:
                kv = att.split(':')
                data[kv[0]] = kv[1]
            call_args['client_kwargs'] = data

        if args.userinfo_endpoint:
            call_args['userinfo_endpoint'] = args.userinfo_endpoint

        if args.client_id:
            call_args['client_id'] = args.client_id

        if args.client_secret:
            call_args['client_secret'] = args.client_secret

        if args.server_metadata_url:
            call_args['server_metadata_url'] = args.server_metadata_url

        response = requests.post(self.get_url() + '/authenticators', headers=headers, json=call_args)
        print(response.json())

class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list available realnet authenticators')

    def add_arguments(self, parser):
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/authenticators', headers=headers)

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
                         'delete a realnet authenticator')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the authenticator to be deleted")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.delete(self.get_url() + '/authenticators/{}'.format(args.name), headers=headers)
        print(response.json())

class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get a realnet authenticator')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the tenant to be retrieved")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/authenticators/{}'.format(args.name), headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Property', 'Value']
            print(Out.format(response.json(), of))

class Update(ProtoCmd, Client):

    def __init__(self):
        super().__init__('update',
                         'update a realnet authenticator')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the authenticator")
        parser.add_argument('--api_base_url', help="specifies the api base url")
        parser.add_argument('--request_token_url', help="specifies the request token url")
        parser.add_argument('--access_token_url', help="specifies the access token url")
        parser.add_argument('--authorize_url', help="specifies the authorize url")
        parser.add_argument('--client_kwarg', action='append', help="specifies the client kwarg name:value")
        parser.add_argument('--userinfo_endpoint', help="specifies the userinfo endpoint")
        parser.add_argument('--client_id', help="specifies the client_id")
        parser.add_argument('--client_secret', help="specifies the client_secret")
        parser.add_argument('--server_metadata_url', help="specifies the server metadata url")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.api_base_url:
            call_args['api_base_url'] = args.api_base_url

        if args.request_token_url:
            call_args['request_token_url'] = args.request_token_url

        if args.access_token_url:
            call_args['access_token_url'] = args.access_token_url

        if args.authorize_url:
            call_args['authorize_url'] = args.authorize_url

        if args.client_kwarg:
            data = dict()
            for att in args.client_kwarg:
                kv = att.split(':')
                data[kv[0]] = kv[1]
            call_args['client_kwargs'] = data

        if args.userinfo_endpoint:
            call_args['userinfo_endpoint'] = args.userinfo_endpoint

        if args.client_id:
            call_args['client_id'] = args.client_id

        if args.client_secret:
            call_args['client_secret'] = args.client_secret

        if args.server_metadata_url:
            call_args['server_metadata_url'] = args.server_metadata_url

        response = requests.put(self.get_url() + '/authenticators/{}'.format(args.name), headers=headers, json=call_args)
        print(response.json())

class Token(ProtoCmd, Client):

    def __init__(self):
        super().__init__('token',
                         'get a new realnet token')

    def add_arguments(self, parser):
        parser.add_argument('--client_key', help="specifies the client key")
        parser.add_argument('--client_secret', help="specifies the client secret")
        parser.add_argument('--username', help="specifies the client key")
        parser.add_argument('--password', help="specifies the client secret")

    def run(self, args):

        call_args = dict()

        if args.client_key:
            call_args['client_key'] = args.client_key

        if args.client_secret:
            call_args['client_secret'] = args.client_secret

        if args.username:
            call_args['username'] = args.username

        if args.password:
            call_args['password'] = args.password

        print(self.generate_token(**call_args))


class Auth(Shell):

        def __init__(self):
            super().__init__('auth')

        def get_commands(self):
            return [
                List(),
                Create(),
                Delete(),
                Get(),
                Update(),
                Token()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Auth shell'