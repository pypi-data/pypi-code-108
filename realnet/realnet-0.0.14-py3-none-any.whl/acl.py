import json

import requests

from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new item acl')

    def convert_type(self, tt):
        t = tt.lower()
        if t == 'public':
            return 1
        elif t == 'group':
            return 2
        else:
            return 3

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item for which the acl is to be created")
        parser.add_argument('name', help="specifies the user or group name to who the acl applies")
        parser.add_argument('type', help="specifies the type of acl (public, group or user)")
        parser.add_argument('permissions', help="specifies the types of permissions that apply: (r)ead, (w)rite,(e)xecute, (m)essage")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        call_args['name'] = args.name
        call_args['type'] = args.type.lower()
        call_args['permission'] = args.permissions

        response = requests.post(self.get_url() + '/items/{}/acls'.format(args.id),
                                 headers=headers,
                                 json=call_args)
        print(response.json())

class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list available item acls')

    def add_arguments(self, parser):
        parser.add_argument('id',
                            help="specifies the id of the item for which to list the acls")
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}


        response = requests.get(self.get_url() + '/items/{}/acls'.format(args.id), headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Name', 'Type', 'Permissions', 'Id']
            of.rows = [
                Extractor('name'), 
                Extractor('type', lambda t: 'public' if t['type'] == 1 else 'group' if t['type'] == '2' else 'user'), 
                Extractor('permission'),
                Extractor('id')]
            print(Out.format(response.json(), of))


class Delete(ProtoCmd, Client):

    def __init__(self):
        super().__init__('delete',
                         'delete an item acl')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('acl_id', help="specifies the id of the acl to be deleted")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.delete(self.get_url() + '/items/{}/acls/{}'.format(args.id, args.acl_id), headers=headers)
        print(response.json())


class Update(ProtoCmd, Client):

    def __init__(self):
        super().__init__('update',
                         'update an item acl')

    def add_arguments(self, parser):
        parser.add_argument('id',
                            help="specifies the id of the item")
        parser.add_argument('acl_id',
                            help="specifies the id of the acl")
        parser.add_argument('name', help="specifies the user or group name to who the acl applies")
        parser.add_argument('type', help="specifies the type of acl (public, group or user)")
        parser.add_argument('permissions',
                            help="specifies the types of permissions that apply: (r)ead, (w)rite,(e)xecute, (m)essage")


    def run(self, args):
            headers = {'Authorization': 'Bearer ' + self.get_token()}

            call_args = dict()
            call_args['name'] = args.name
            call_args['type'] = args.type
            call_args['permission'] = args.permissions

            response = requests.put(self.get_url() + '/items/{}/acls/{}'.format(args.id, args.acl_id),
                                     headers=headers,
                                     json=call_args)
            print(response.json())

class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get an acl')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('acl_id', help="specifies the id of the acl to be retrieved")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/items/{}/acls/{}'.format(args.id, args.acl_id), headers=headers)
        print(response.json())


class Acl(Shell):

        def __init__(self):
            super().__init__('acl')

        def get_commands(self):
            return [
                List(),
                Create(),
                Delete(),
                Update(),
                Get()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Acl shell'