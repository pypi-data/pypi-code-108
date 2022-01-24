from functools import cached_property
from typing import Generator, List

from deepdiff import DeepDiff


class ReplaceElement(Exception):
    def __init__(self, data):
        super().__init__()
        self.data = data


class ModelBuilderStackEntry:
    def __init__(self, key=None, data=None):
        self.key = key
        self.data = data

    def __getitem__(self, item):
        return self.data[item]

    def __eq__(self, other):
        return self.key == other.key and not DeepDiff(self.key, other.key)

    def __str__(self):
        return f'{self.key} - {self.data}'


class ModelBuilderStack:
    DICT = 'dict'
    LIST = 'list'
    PRIMITIVE = 'primitive'
    SKIP = 'skip'

    def __init__(self, schema):
        self.schema = schema
        self.stack = []

    def __getitem__(self, item):
        return self.stack[item]

    def push(self, key, el):
        self._clear_path()
        self.stack.append(ModelBuilderStackEntry(key, el))

    def pop(self):
        self._clear_path()
        self.stack.pop()

    @property
    def top(self):
        return self.stack[-1]

    @property
    def level(self):
        return len(self.stack)

    @property
    def top_type(self):
        match self.top.data:
            case dict():
                return self.DICT
            case list():
                return self.LIST
            case _:
                return self.PRIMITIVE

    @cached_property
    def path(self):
        return '/' + '/'.join(x.key for x in self.stack if x.key)

    def _clear_path(self):
        if "path" in self.__dict__:
            del self.__dict__["path"]

    def process(self, on_element):
        self.stack = []
        try:
            processing_order = self.schema.schema.processing_order
        except AttributeError:
            processing_order = None
        self._process_internal(None, self.schema.schema, on_element, processing_order)

    def _process_internal(self, key, element, on_element, processing_order: List[str] = None):
        popped = False

        try:
            # push the element to the stack
            self.push(key, element)

            # call the on_element function.
            ret = on_element(self)

            # if the result is not a generator,
            if not isinstance(ret, Generator):
                ret = iter([ret])

            res = next(ret, '')

            if res is self.SKIP:
                return

            match self.top_type:
                case self.LIST:
                    for idx, l in enumerate(self.top.data):
                        self._process_internal(idx, l, on_element)
                case self.DICT:
                    items = list(self.top.data.items())
                    if processing_order:
                        def key_function(x):
                            try:
                                return processing_order.index(x)
                            except ValueError:
                                pass
                            try:
                                return processing_order.index('*')
                            except ValueError:
                                pass
                            return len(processing_order)

                        items.sort(key=key_function)
                    for k, v in items:
                        self._process_internal(k, v, on_element)

            next(ret, '')

        except ReplaceElement as re:
            self.pop()
            popped = True
            for k, v in re.data.items():
                self._process_internal(k, v, on_element)
        finally:
            if not popped:
                self.pop()
