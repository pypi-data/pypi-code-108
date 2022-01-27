#!/usr/bin/env python3
import inspect
from collections import deque

import quickspider.core.Node
import quickspider.core.nodes
from quickspider.core.Node import BaseNode

# scan the node class in nodes
node_class = {"basenode": quickspider.core.Node.BaseNode}


def add_node_class(module):
    global node_class
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj,
                                               quickspider.core.Node.BaseNode):
            node_class[name.lower()] = obj


add_node_class(quickspider.core.Node)
add_node_class(quickspider.core.nodes)


class Builder:
    node_class = node_class

    def __init__(self):
        self._nodes = deque()

    def _add_node(self, _node):
        self._nodes.append(_node)

    def node_build(self, _name, _config):
        node_class_name = _config.pop("type").lower()
        node_class = Builder.get_class_from_name(node_class_name)
        config = {f"_{k}": v for k, v in _config.items()}
        name = _name.split(".")[-1]
        node = node_class(_name=name, **config)
        self._add_node(node)
        return node

    def link(self):
        header = BaseNode("header")
        node = header
        while self._nodes:
            next_node = self._nodes.popleft()
            node = node.add_child(next_node)
        return header

    @staticmethod
    def get_class_from_name(node_class_name):
        return Builder.node_class.get(node_class_name, BaseNode)


if __name__ == "__main__":
    b = Builder()
