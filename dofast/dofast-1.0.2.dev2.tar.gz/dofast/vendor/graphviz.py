import os
import tempfile
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Union

import codefast as cf


class Graphviz(ABC):
    @abstractmethod
    def draw(self) -> str:
        ''''''


class Record(Graphviz):
    def __init__(self, background_color: str = ''):
        self.prefix = '''digraph { graph[dpi=300];'''
        self.suffix = '}'
        self.record_prefix = 'n[shape=record,style=rounded,label="'
        if background_color:
            self.record_prefix = 'n[shape=record,filled={},style="rounded,filled",label="'.format(
                background_color)

    def draw(self) -> str:
        ''''''

    def extract_command_from_list(self, list_: List[Tuple[str]]) -> str:
        cf.info('Draw record from list {}'.format(list_))
        dot_cmd = []
        for col in range(len(list_[0])):
            lst = [e[col] for e in list_]
            dot_cmd.append('{' + ' | '.join(map(lambda e: str(e) + '\l', lst)) +
                           '}')
        return self.record_prefix + '|'.join(dot_cmd) + '"];'

    def draw_from_list(self, list_: List[Tuple[str]]) -> str:
        cmd = [self.prefix, self.extract_command_from_list(list_), self.suffix]
        cmd = ''.join(cmd)
        uuid = cf.uuid()
        png_name = '/tmp/{}.png'.format(uuid)
        cf.info('Draw record from list {}, uuid {}'.format(list_, uuid))
        with tempfile.NamedTemporaryFile(suffix='.dot') as f:
            f.write(cmd.encode())
            f.flush()
            os.system('dot -Tpng -o {} {}'.format(png_name, f.name))
            if cf.io.exists(png_name):
                return png_name
        return ''


if __name__ == '__main__':
    list_ = [('TIME', 'DATE', 'DESCRIPTION'), ('time', 'date', 'description'),
             ('time', 'date', 'A quite long sentence for indent....')]

    rc = Record(background_color='lightblue')
    s = rc.draw_from_list(list_)
    print(s)
