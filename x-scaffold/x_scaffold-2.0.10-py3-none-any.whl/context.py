import os

from typing import Dict, List


class ScaffoldContext(dict):
    notes: List[str]
    todos: List[str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['steps'] = {}
        self['colors'] = {
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
        self.notes = []
        self.todos = []

    def resolve_package_path(self, path):
        package_dir = self['__package']['path']
        return os.path.realpath(os.path.join(package_dir, path))

    def resolve_target_path(self, path):
        target_dir = self['__target']
        return os.path.realpath(os.path.join(target_dir, path))
    
    def set_step(self, step_id, value):
        self['steps'][step_id] = value
