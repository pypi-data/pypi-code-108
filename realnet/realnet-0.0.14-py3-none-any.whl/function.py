import requests

from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new realnet function')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item or topic under which the function is to be created")
        parser.add_argument('name', help="specifies the name of the function to be created")
        parser.add_argument('path', help="specifies the path of the file that contains the function code")
        parser.add_argument('--topic', help="specifies the name of the topic to associate with the function")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        call_args['name'] = args.name

        with open(args.path, 'r') as f:
            call_args['code'] = f.read()

        if args.topic:
            response = requests.post(self.get_url() + '/items/{}/topics/{}/functions'.format(args.id, args.topic),
                                     headers=headers,
                                     json=call_args)
        else:
            response = requests.post(self.get_url() + '/items/{}/functions'.format(args.id),
                                     headers=headers,
                                     json=call_args)
        print(response.json())

class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list available item functions')

    def add_arguments(self, parser):
        parser.add_argument('id',
                            help="specifies the id of the item or topic for which to list the functions")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")
        parser.add_argument('--topic', help="specifies the name of the topic to associate with the function")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        if args.topic:
            response = requests.get(self.get_url() + '/items/{}/topics/{}/functions'.format(args.id, args.topic),
                                     headers=headers)
        else:
            response = requests.get(self.get_url() + '/items/{}/functions'.format(args.id), headers=headers)

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
                         'delete a function')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('name', help="specifies the name of the function to be deleted")
        parser.add_argument('--topic', help="specifies the name of the topic associated with the function")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        if args.topic:
            response = requests.delete(self.get_url() + '/items/{}/topics/{}/functions/{}'.format(args.id, args.topic, args.name),
                                       headers=headers)
        else:
            response = requests.delete(self.get_url() + '/items/{}/functions/{}'.format(args.id, args.name), headers=headers)

        print(response.json())


class Update(ProtoCmd, Client):

    def __init__(self):
        super().__init__('update',
                         'update a realnet function')

    def add_arguments(self, parser):
        parser.add_argument('id',
                            help="specifies the id of the item or topic")
        parser.add_argument('name', help="specifies the name of the function to be updated")
        parser.add_argument('path', help="specifies the path of the file that contains the function code")
        parser.add_argument('--topic', help="specifies the name of the topic associated with the function")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        with open(args.path, 'r') as f:
            call_args['code'] = f.read()

        if args.topic:
            response = requests.put(self.get_url() + '/items/{}/topics/{}/functions/{}'.format(args.id, args.topic, args.name),
                                    headers=headers,
                                    json=call_args)
        else:
            response = requests.put(self.get_url() + '/items/{}/functions/{}'.format(args.id, args.name),
                                     headers=headers,
                                     json=call_args)
        print(response.json())

class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get a function')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('name', help="specifies the name of the function to be retrieved")
        parser.add_argument('--topic', help="specifies the name of the topic associated with the function")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        if args.topic:
            response = requests.get(self.get_url() + '/items/{}/topics/{}/functions/{}'.format(args.id, args.topic, args.name), headers=headers)
        else:
            response = requests.get(self.get_url() + '/items/{}/functions/{}'.format(args.id, args.name),
                                    headers=headers)
        print(response.json())

class Invoke(ProtoCmd, Client):

    def __init__(self):
        super().__init__('invoke',
                         'invoke a function')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('name', help="specifies the name of the function to be invoked")
        parser.add_argument('--argument', action='append', help="specifies the argument name:value")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.argument:
            for att in args.argument:
                kv = att.split(':')
                call_args[kv[0]] = kv[1]

        response = requests.post(self.get_url() + '/items/{}/functions/{}'.format(args.id, args.name),
                                 headers=headers,
                                 json=call_args)
        print(response.json())


class Function(Shell):

        def __init__(self):
            super().__init__('function')

        def get_commands(self):
            return [
                List(),
                Create(),
                Delete(),
                Update(),
                Get(),
                Invoke()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Function shell'