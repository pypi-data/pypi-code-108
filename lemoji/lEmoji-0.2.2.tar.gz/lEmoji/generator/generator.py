import json
import os

from lEmoji.generator.web_extractor import WebExtractor
from lEmoji.data.tree import tree


class Generator:
    def __init__(self, proxies=None):
        self.extractor = WebExtractor(proxies=proxies)
        self.tree = self.extractor.build()
        self.working_dir = os.path.join(os.getcwd(), 'lEmoji')
        self.data_file = os.path.join(os.getcwd(), 'lEmoji', 'data', 'tree.py')

    @staticmethod
    def find_node(node_list, name):
        for node in node_list:
            if node['name'] == name:
                return node

    def generate(self, his_nodes=None, cur_nodes=None, version=None):
        if not version:
            his_nodes = tree
            cur_nodes = self.tree
        else:
            version = version.replace('.', '_')

        emoji_list = []

        for node in cur_nodes:
            his_node = self.find_node(his_nodes, node['name'])
            if node['type'] == 'folder':
                if not his_node:
                    self.generate([], node['children'], version=node['name'])
                elif node['time'] != his_node['time']:
                    self.generate(his_node['children'], node['children'], version=node['name'])
            elif node['name'].startswith('emoji'):
                emoji_list.extend(self.extractor.emoji_fetcher(node['link']))

        if version:
            path = os.path.join(self.working_dir, 'emoji_v%s.py' % version)
            emoji_list = list(set(emoji_list))
            with open(path, 'wb+') as f:
                s = 'EMOJI_LIST = ' + json.dumps(emoji_list, ensure_ascii=False)
                f.write(s.encode())
        else:
            with open(self.data_file, 'wb+') as f:
                s = 'tree = ' + json.dumps(cur_nodes, ensure_ascii=False) + '\n'
                f.write(s.encode())
            with open(os.path.join(self.working_dir, '__init__.py'), 'wb+') as f:
                for node in cur_nodes:
                    name = node['name'].replace('.', '_')
                    s = 'from .emoji_v%s import EMOJI_LIST as EMOJI_LIST_%s\n' % (
                        name, name.upper())
                    f.write(s.encode())

                s = '\n\nEMOJI_LIST = EMOJI_LIST_%s\n' % \
                    cur_nodes[-1]['name'].replace('.', '_').upper()
                f.write(s.encode())
