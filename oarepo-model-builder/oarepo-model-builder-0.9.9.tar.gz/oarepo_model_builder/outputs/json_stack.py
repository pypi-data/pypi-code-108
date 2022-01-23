import copy
from typing import List

from oarepo_model_builder.utils.deepmerge import deepmerge


class JSONStack:
    """Hierarchic json builder."""
    IGNORED_SUBTREE = object()
    IGNORED_NODE = object()

    def __init__(self):
        self.stack: List = [{}]

    def should_ignore(self, element):
        return element is self.IGNORED_SUBTREE or element is self.IGNORED_NODE

    def push(self, key, el):
        if key is None:
            assert isinstance(el, dict)
            assert self.empty
            self.stack[0] = deepmerge(copy.deepcopy(el), self.stack[0], [])
            return
        top = self.stack[-1]
        if top is self.IGNORED_SUBTREE:
            self.stack.append(self.IGNORED_SUBTREE)
        elif self.should_ignore(el):
            self.stack.append(el)
        else:
            if top is self.IGNORED_NODE:
                top = self.real_top

            el = copy.deepcopy(el)
            if isinstance(top, dict):
                if key not in top:
                    top[key] = el
                else:
                    top[key] = deepmerge(el, top[key])
            elif isinstance(top, list):
                if key < len(top):
                    top[key] = deepmerge(el, top[key])
                else:
                    assert key == len(top)
                    top.append(el)
            else:
                raise NotImplemented(f'Set for datatype {type(top)} is not implemented')
            self.stack.append(el)

    def pop(self):
        if not self.empty:
            self.stack.pop()

    @property
    def empty(self):
        return len(self.stack) == 1

    @property
    def value(self):
        return self.stack[0]

    @property
    def real_top(self):
        for t in reversed(self.stack):
            if t is not self.IGNORED_NODE:
                return t

    def merge(self, value):
        real_top = self.real_top
        real_top.update(deepmerge(value, real_top, []))
