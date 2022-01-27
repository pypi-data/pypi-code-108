import json

from deepdiff import DeepDiff

from . import OutputBase
from .json_stack import JSONStack
from ..utils.verbose import log

import yaml


class YAMLOutput(OutputBase):
    IGNORE_NODE = JSONStack.IGNORED_NODE
    IGNORE_SUBTREE = JSONStack.IGNORED_SUBTREE
    TYPE = 'yaml'

    def begin(self):
        self._created = True
        try:
            with self.builder.filesystem.open(self.path) as f:
                self.original_data = yaml.load_all(f, yaml.SafeLoader)  # noqa
                self._created = False
        except FileNotFoundError:
            self.original_data = None
        except ValueError:
            self.original_data = None

        self.stack = JSONStack()
        self.documents = []

    def next_document(self):
        if self.stack.value:
            self.documents.append(self.stack.value)
            self.stack = JSONStack()

    def finish(self):
        self.next_document()

        if not self.documents and self.original_data:
            # nothing generated, keep the file
            return

        self._created = False
        if DeepDiff(self.documents, self.original_data):
            self.builder.filesystem.mkdir(self.path.parent)
            log(2, 'Saving %s', self.path)
            with self.builder.filesystem.open(self.path, mode='w') as f:
                yaml.safe_dump_all(self.documents, f)

    @property
    def created(self):
        return self._created

    @created.setter
    def created(self, value):
        self._created = value

    def enter(self, key, el):
        if key:
            self.stack.push(key, el)

    def leave(self):
        if not self.stack.empty:
            self.stack.pop()

    def primitive(self, key, value):
        if key:
            self.stack.push(key, value)
            self.stack.pop()

    def merge(self, value):
        self.stack.merge(value)
