import json

from deepdiff import DeepDiff

from . import OutputBase
from .json_stack import JSONStack
from ..utils.verbose import log

try:
    import json5
except ImportError:
    import json as json5


class JSONOutput(OutputBase):
    IGNORE_NODE = JSONStack.IGNORED_NODE
    IGNORE_SUBTREE = JSONStack.IGNORED_SUBTREE
    TYPE = 'json'

    def begin(self):
        try:
            with self.builder.filesystem.open(self.path) as f:
                self.original_data = json5.load(f)  # noqa
        except FileNotFoundError:
            self.original_data = None
        except ValueError:
            self.original_data = None

        self.stack = JSONStack()

    @property
    def created(self):
        return self.original_data is None

    def finish(self):
        data = self.stack.value
        if DeepDiff(data, self.original_data):
            self.builder.filesystem.mkdir(self.path.parent)
            log(2, 'Saving %s', self.path)
            with self.builder.filesystem.open(self.path, mode='w') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

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
