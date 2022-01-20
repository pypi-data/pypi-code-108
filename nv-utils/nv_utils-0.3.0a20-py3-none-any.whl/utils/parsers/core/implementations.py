from typing import Any

from .parser import build_parser, UnknownParser, remove_all, remove_empty


class Visitor:
    def __init__(self,
                 tracking=False,
                 behaviour: UnknownParser.Behaviour = UnknownParser.Behaviour.IGNORE,
                 **parser_kwargs):

        self._tracking = tracking
        self._behaviour = behaviour
        self.visited_nodes = []

        self.visit = build_parser(self.visitor, behaviour=behaviour, **parser_kwargs)

    def visitor(self, node: Any, _, **kwargs):
        if self._tracking:
            self.visited_nodes.append(node)
        return node


visitor = Visitor(debug=False, behaviour=UnknownParser.Behaviour.RAISE)


def visit_nodes(obj, **parser_kwargs):
    _visitor = Visitor(tracking=True, **parser_kwargs)
    _visitor.visit(obj)
    return _visitor.visited_nodes


class Cleaner(Visitor):
    def __init__(self, remove_none: bool = False, **parser_kwargs):
        parser_kwargs['wrapper'] = remove_all if remove_none else remove_empty
        super().__init__(**parser_kwargs)
        self.clean = self.visit


cleaner = Cleaner(debug=True)


def clean_nodes(obj, **parser_kwargs):
    _cleaner = Cleaner(**parser_kwargs)
    return _cleaner.clean(obj)
