from getpass import getpass
from typing import Dict, List
import sys
import click

from x_scaffold.context import ScaffoldContext

CLI_COLORS = {
    'PURPLE': '\033[35m',
    'CYAN':  '\033[36m',
    'BLUE':  '\033[34m',
    'GREEN':  '\033[32m',
    'YELLOW':  '\033[33m',
    'RED':  '\033[31m',
    'BOLD':  '\033[1m',
    'UNDERLINE':  '\033[4m',
    'ITALIC':  '\033[3m',
    'END':  '\033[0m',
}

class ScaffoldRuntime:
    def write(self, message: str):
        pass

    def ask(self, prompt):
        pass

    def print_todos(self, context: ScaffoldContext):
        pass

    def print_notes(self, context: ScaffoldContext):
        pass


class ScaffoldConsoleRuntime(ScaffoldRuntime):
    def log(self, message):
        self.write(message + '\n')

    def ask(self, prompt):
        name = prompt.get('name')
        description = prompt.get('description', name)
        if 'choices' in prompt:
            choices = prompt['choices']
            opts = []
            max_len = 0
            for c in choices:
                if isinstance(c, str):
                    opts.append({
                        't': c,
                        'kw': [c],
                        'v': c
                    })
                else:
                    keywords = ', '.join(c['keywords'])
                    if len(keywords) > max_len:
                        max_len = len(keywords)
                    opts.append({
                        'kw': c['keywords'],
                        'kwt': keywords,
                        't': c['text'],
                        'v': c.get('value', c['text'])
                    })

            self.write(description + ': \n')
            for opt in opts:
                if 'kwt' in opt:
                    opt['kwt'] = opt['kwt'].ljust(max_len)
                    self.write('  - [{kwt}] {t}\n'.format(**opt))
                else:
                    self.write(f'  - {opt["t"]}\n')

            choice = input('Choose: ')
            while True:
                for c in opts:
                    if choice in c['kw']:
                        return c['v']
                self.write('{RED}[invalid choice]{END} Choose: ')
                choice = sys.stdin.readline().strip()

        if prompt.get('secure', False):
            return getpass(prompt=description + ': ')
        else:
            self.write(description + ': ')
            return sys.stdin.readline().strip()
    
    def write(self, message: str):
        sys.stdout.write(message.format(**CLI_COLORS))
        sys.stdout.flush()

    def print_todos(self, context: ScaffoldContext):
        self.write('{BLUE}{BOLD}TODO:{END}\n')
        for todo in context.todos:
            self.write(f'  - {todo}\n')

    def print_notes(self, context: ScaffoldContext):
        self.write('{GREEN}{BOLD}NOTES:{END}\n')
        for note in context.notes:
            self.write(f'  {note}\n')

