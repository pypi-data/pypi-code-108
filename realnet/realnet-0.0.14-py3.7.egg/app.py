import requests

from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new realnet app')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the app")
        parser.add_argument('uri', help="specifies the uri for the app")
        parser.add_argument('--auth_method', help="specifies the token endpoint authentication method for the app (none, client_secret_basic, client_secret_post)", default="none")
        parser.add_argument('--grant_type',  action='append', help="specifies the grant type for the app (authorization_code, password, implicit, client_credentials)")
        parser.add_argument('--redirect_uri', action='append', help="specifies the redirect uri for the app")
        parser.add_argument('--response_type', action='append', help="specifies the response type for the app (code, token)")
        parser.add_argument('--scope', action='append', help="specifies the scope for the app")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        call_args['name'] = args.name
        call_args['uri'] = args.uri
        call_args['auth_method'] = args.auth_method

        if args.grant_type:
            call_args['grant_types'] = args.grant_type
        else:
            call_args['grant_types'] = []

        if args.redirect_uri:
            call_args['redirect_uris'] = args.redirect_uri
        else:
            call_args['redirect_uris'] = []

        if args.response_type:
            call_args['response_types'] = args.response_type
        else:
            call_args['response_types'] = []

        if args.scope:
            call_args['scope'] = args.scope
        else:
            call_args['scope'] = ''

        response = requests.post(self.get_url() + '/apps', headers=headers, json=call_args)
        print(response.json())

class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list available realnet apps')

    def add_arguments(self, parser):
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/apps', headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['name', 'client_id', 'id']
            of.rows = [Extractor('name'), Extractor('client_id'), Extractor('id')]
            print(Out.format(response.json(), of))

class Delete(ProtoCmd, Client):

    def __init__(self):
        super().__init__('delete',
                         'delete a realnet app')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the app to be deleted")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.delete(self.get_url() + '/apps/{}'.format(args.id), headers=headers)
        print(response.json())

class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get a realnet app')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the name of the app to be retrieved")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/apps/{}'.format(args.id), headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Property', 'Value']
            print(Out.format(response.json(), of))

class Update(ProtoCmd, Client):

    def __init__(self):
        super().__init__('update',
                         'update a realnet app')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the app")
        parser.add_argument('--uri', help="specifies the uri for the app")
        parser.add_argument('--auth_method', help="specifies the token endpoint authentication method for the app")
        parser.add_argument('--grant_type', action='append', help="specifies the grant type for the app")
        parser.add_argument('--redirect_uri', action='append', help="specifies the redirect uri for the app")
        parser.add_argument('--response_type', action='append', help="specifies the response type for the app")
        parser.add_argument('--scope', action='append', help="specifies the scope for the app")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.uri:
            call_args['uri'] = args.uri

        if args.auth_method:
            call_args['auth_method'] = args.auth_method

        if args.grant_type:
            call_args['grant_types'] = args.grant_type

        if args.redirect_uri:
            call_args['redirect_uris'] = args.redirect_uri

        if args.response_type:
            call_args['response_types'] = args.response_type

        if args.scope:
            call_args['scope'] = args.scope

        response = requests.put(self.get_url() + '/apps/{}'.format(args.name), headers=headers, json=call_args)
        print(response.json())


class App(Shell):

        def __init__(self):
            super().__init__('app')

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
            return 'App shell'