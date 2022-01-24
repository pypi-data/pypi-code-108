import os

from typing import Dict, List


class ScaffoldContext(dict):
    notes: List[str]
    todos: List[str]
    environ: Dict[str, str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notes = []
        self.todos = []
        self.environ = {}

    def resolve_package_path(self, path):
        package_dir = self['__package']['path']
        return os.path.realpath(os.path.join(package_dir, path))

    def resolve_target_path(self, path):
        target_dir = self['__target']
        return os.path.realpath(os.path.join(target_dir, path))
