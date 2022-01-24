import requests

from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new realnet type')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the type")
        # parser.add_argument('--parent', help="specifies the id of the parent item")
        parser.add_argument('--icon', help="specifies the type icon name")
        parser.add_argument('--attribute', action='append', help="specifies the attribute name:value")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.name:
            call_args['name'] = args.name

        if args.icon:
            call_args['icon'] = args.icon

        if args.attribute:
            data = dict()
            for att in args.attribute:
                kv = att.split(':')
                data[kv[0]] = kv[1]
            call_args['attributes'] = data

        response = requests.post(self.get_url() + '/types', headers=headers, json=call_args)
        print(response.json())

class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list available realnet types')

    def add_arguments(self, parser):
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/types', headers=headers)

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
                         'delete a realnet type')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the type to be deleted")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.delete(self.get_url() + '/types/{}'.format(args.id), headers=headers)
        print(response.json())

class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get a realnet type')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the type to be retrieved")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/types/{}'.format(args.id), headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Property', 'Value']
            print(Out.format(response.json(), of))

class Update(ProtoCmd, Client):

    def __init__(self):
        super().__init__('update',
                         'update a realnet type')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the type")
        parser.add_argument('--rename', help="specifies the new name of the type")
        parser.add_argument('--icon', help="specifies the icon of the type")
        parser.add_argument('--attribute', action='append', help="specifies the attribute name:value")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.rename:
            call_args['name'] = args.rename

        if args.icon:
            call_args['icon'] = args.icon

        if args.attribute:
            data = dict()
            for att in args.attribute:
                kv = att.split(':')
                data[kv[0]] = kv[1]
            call_args['attributes'] = data

        response = requests.put(self.get_url() + '/types/{}'.format(args.name), headers=headers, json=call_args)
        print(response.json())

class Type(Shell):

        def __init__(self):
            super().__init__('type')

        def get_commands(self):
            return [
                List(),
                Create(),
                Update(),
                Get(),
                Delete()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Type shell'