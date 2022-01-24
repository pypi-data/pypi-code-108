import requests
import re
import os
from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor


from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new realnet item')

    def add_arguments(self, parser):
        parser.add_argument('type', help="specifies the type of the item")
        parser.add_argument('name', help="specifies the name of the item")
        parser.add_argument('--parent', help="specifies the id of the parent item")
        parser.add_argument('--attribute', action='append', help="specifies the attribute name:value")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.parent:
            call_args['parent_id'] = args.parent

        if args.type:
            call_args['type'] = args.type

        if args.name:
            call_args['name'] = args.name

        if args.attribute:
            data = dict()
            for att in args.attribute:
                kv = att.split(':')
                data[kv[0]] = kv[1]
            call_args['attributes'] = data

        response = requests.post(self.get_url() + '/items', headers=headers, json=call_args)
        print(response.json())

class Delete(ProtoCmd, Client):

    def __init__(self):
        super().__init__('delete',
                         'delete a realnet item')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item to be deleted")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.delete(self.get_url() + '/items/{}'.format(args.id), headers=headers)
        print(response.json())

class Find(ProtoCmd):

    def __init__(self):
        super().__init__('find',
                         'find a realnet item')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the API")
        parser.add_argument('url', help="specifies the url of the API")

    def run(self, args):
        pass

class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get a realnet item')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item to be retrieved")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/items/{}'.format(args.id), headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Property', 'Value']
            print(Out.format(response.json(), of))

class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list children of a realnet item')

    def add_arguments(self, parser):
        parser.add_argument('--id', help="specifies the id of the item to be listed")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}
        if args.id:
            response = requests.get(self.get_url() + '/items/{}/items'.format(args.id), headers=headers)
        else:
            response =  requests.get(self.get_url() + '/items', headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Name', 'Type', 'Id']
            of.rows = [Extractor('name'), Extractor('type', lambda x: x['type']['name']), Extractor('id')]
            print(Out.format(response.json(), of))

class Update(ProtoCmd, Client):

    def __init__(self):
        super().__init__('update',
                         'update a realnet item')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('--name', help="specifies the name of the item")
        parser.add_argument('--parent', help="specifies the id of the parent item")
        parser.add_argument('--attribute', action='append', help="specifies the attribute name:value")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.parent:
            call_args['parent_id'] = args.parent

        if args.name:
            call_args['name'] = args.name

        if args.attribute:
            data = dict()
            for att in args.attribute:
                kv = att.split(':')
                data[kv[0]] = kv[1]
            call_args['attributes'] = data

        response = requests.put(self.get_url() + '/items/{}'.format(args.id), headers=headers, json=call_args)
        print(response.json())

class Upload(ProtoCmd, Client):

    def __init__(self):
        super().__init__('upload',
                         'upload item data')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('path', help="specifies the path of the file to be uploaded")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.post(self.get_url() + '/items/{}/data'.format(args.id), headers=headers, files={'file': open(args.path, 'rb')})
        print(response.json())


class Download(ProtoCmd, Client):

    def __init__(self):
        super().__init__('download',
                         'download item data')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('--path', help="specifies the target path for the file to be downloaded")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/items/{}/data'.format(args.id), headers=headers)
        d = response.headers['content-disposition']
        filename = re.findall("filename=(.+)", d)[0]

        path = filename
        if args.path:
            path = os.path.join(args.path, filename)

        # print([i for i in response.__dict__.items() if i[0] != '_content'])
        with open(path, 'wb') as f:
            f.write(response.content)



class Item(Shell):

        def __init__(self):
            super().__init__('item')

        def get_commands(self):
            return [
                Create(),
                Delete(),
                Get(),
                List(),
                Find(),
                Update(),
                Upload(),
                Download()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Item shell'