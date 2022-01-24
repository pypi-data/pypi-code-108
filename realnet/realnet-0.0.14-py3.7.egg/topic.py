import json

import requests

from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new realnet topic')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item under which the topic is to be created")
        parser.add_argument('name', help="specifies the name of the topic to be created")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        call_args['name'] = args.name

        response = requests.post(self.get_url() + '/items/{}/topics'.format(args.id),
                                 headers=headers,
                                 json=call_args)
        print(response.json())

class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list available item topics')

    def add_arguments(self, parser):
        parser.add_argument('id',
                            help="specifies the id of the item or topic for which to list the functions")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}


        response = requests.get(self.get_url() + '/items/{}/topics'.format(args.id), headers=headers)

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
                         'delete a topic')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('name', help="specifies the name of the topic to be deleted")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.delete(self.get_url() + '/items/{}/topics/{}'.format(args.id, args.name), headers=headers)
        print(response.json())


class Update(ProtoCmd, Client):

    def __init__(self):
        super().__init__('update',
                         'update a realnet topic')

    def add_arguments(self, parser):
        parser.add_argument('id',
                            help="specifies the id of the item")
        parser.add_argument('name', help="specifies the name of the topic to be updated")

        parser.add_argument('data', help="specifies the topic data")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()
        call_args['data'] = args.data

        response = requests.put(self.get_url() + '/items/{}/topics/{}'.format(args.id, args.name),
                                 headers=headers,
                                 json=call_args)
        print(response.json())

class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get a topic')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('name', help="specifies the name of the topic to be retrieved")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/items/{}/topics/{}'.format(args.id, args.name), headers=headers)
        print(response.json())

class Send(ProtoCmd, Client):

    def __init__(self):
        super().__init__('send',
                         'send message to topic')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('name', help="specifies the name of the topic")
        parser.add_argument('data', help="specifies the message json data")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.post(self.get_url() + '/items/{}/topics/{}'.format(args.id, args.name),
                                 headers=headers,
                                 json=json.loads(args.data))
        print(response.json())


class Messages(ProtoCmd, Client):

    def __init__(self):
        super().__init__('messages',
                         'receive topic messages')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('name', help="specifies the name of the topic")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/items/{}/topics/{}'.format(args.id, args.name),
                                 headers=headers)
        print(response.json())


class Topic(Shell):

        def __init__(self):
            super().__init__('topic')

        def get_commands(self):
            return [
                List(),
                Create(),
                Delete(),
                Update(),
                Get(),
                Send(),
                Messages()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Topic shell'