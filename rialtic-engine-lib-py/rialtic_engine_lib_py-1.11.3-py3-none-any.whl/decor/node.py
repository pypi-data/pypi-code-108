from typing import Union

from enginelib.simple_insight import SimpleInsight
from enginelib.decor.predicate import Predicate

Label = Union[int, str]


class AbstractNode:
    label: Label

    def print(self, indent: str = '', end: bool = False):
        """Prints the given tree / subtree recursively.
        """
        pass


class DecisionNode(AbstractNode):
    def __init__(self, label: Label, predicate: Predicate, yes_node: AbstractNode, no_node: AbstractNode):
        self.label = label
        self.predicate = predicate
        self.yes_node = yes_node
        self.no_node = no_node

    def print(self, indent: str = '', end: bool = False):
        print(indent, self.label, repr(self.predicate.func.__doc__))
        if end:
            new_indent = indent[:-4] + '    ' if indent else ''
            self.yes_node.print(new_indent + ' ├──')
            self.no_node.print(new_indent + ' └──', True)
        else:
            new_indent = indent[:-4] + ' │  ' if indent else ''
            self.yes_node.print(new_indent + ' ├──')
            self.no_node.print(new_indent + ' └──', True)


class LeafNode(AbstractNode):
    def __init__(self, label: Label, simple_insight: SimpleInsight):
        self.simple_insight = simple_insight
        self.label = label

    def print(self, indent: str = '', end: bool = False):
        print(indent, self.label, repr(self.simple_insight.text))
