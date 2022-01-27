import copy
from typing import TYPE_CHECKING, Union


__all__ = ("Query", "LogicalCombination")


if TYPE_CHECKING:
    from .models import MongoModel


def _validate_query_data(model: 'MongoModel', query: dict) -> dict:
    return model._validate_query_data(query)


class QueryNodeVisitor(object):
    """Base visitor class for visiting Query-object nodes in a query tree."""

    def prepare_combination(
        self, combination: 'LogicalCombination'
    ) -> Union['LogicalCombination', dict]:
        """Called by LogicalCombination objects."""
        return combination

    def visit_query(self, query: 'Query') -> Union['Query', dict]:
        """Called by (New)Query objects."""
        return query


class SimplificationVisitor(QueryNodeVisitor):
    def __init__(self, model: 'MongoModel'):
        self.model = model

    def prepare_combination(
        self, combination: 'LogicalCombination'
    ) -> Union['LogicalCombination', dict]:
        if combination.operation == combination.AND:
            # The simplification only applies to 'simple' queries
            if all(isinstance(node, Query) for node in combination.children):
                queries = [n.query for n in combination.children]
                query = self._query_conjunction(queries)
                return {"$and": query}

        return combination

    def _query_conjunction(self, queries):
        """Merges query dicts - effectively &ing them together."""
        combined_query = []
        for query in queries:
            query = _validate_query_data(self.model, query)
            combined_query.append(copy.deepcopy(query))
        return combined_query


class QueryCompilerVisitor(QueryNodeVisitor):
    """Compiles the nodes in a query tree to a PyMongo-compatible query
    dictionary.
    """

    def __init__(self, model):
        self.model = model

    def prepare_combination(
        self, combination: 'LogicalCombination'
    ) -> Union['LogicalCombination', dict]:
        operator = "$and"
        if combination.operation == combination.OR:
            operator = "$or"
        return {operator: combination.children}

    def visit_query(self, query: 'Query') -> Union['Query', dict]:
        data = _validate_query_data(self.model, query.query)
        return data


class QueryNode(object):
    """Base class for nodes in query trees."""

    AND = 0
    OR = 1

    def to_query(self, model: 'MongoModel') -> dict:
        query = self.accept(SimplificationVisitor(model))
        if not isinstance(query, dict):
            query = query.accept(QueryCompilerVisitor(model))
        return query

    def accept(self, visitor):
        raise NotImplementedError

    def _combine(self, other, operation):
        """Combine this node with another node into a LogicalCombination
        object.
        """
        # If the other Query() is empty, ignore it and just use `self`.
        if getattr(other, "empty", True):
            return self

        # Or if this Q is empty, ignore it and just use `other`.
        if self.empty:
            return other

        return LogicalCombination(operation, [self, other])

    @property
    def empty(self):
        return False

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)


class LogicalCombination(QueryNode):
    def __init__(self, operation, children):
        self.operation = operation
        self.children = []
        for node in children:
            # If the child is a combination of the same type, we can merge its
            # children directly into this combinations children
            if isinstance(node, LogicalCombination) and node.operation == operation:
                self.children += node.children
            else:
                self.children.append(node)

    def __repr__(self):
        op = " & " if self.operation is self.AND else " | "
        return "(%s)" % op.join([repr(node) for node in self.children])

    def __bool__(self):
        return bool(self.children)

    def accept(self, visitor) -> Union['LogicalCombination', dict]:
        for i in range(len(self.children)):
            if isinstance(self.children[i], QueryNode):
                self.children[i] = self.children[i].accept(visitor)

        return visitor.prepare_combination(self)

    @property
    def empty(self):
        return not bool(self.children)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__
            and self.operation == other.operation
            and self.children == other.children
        )


class Query(QueryNode):
    """A simple query object, used in a query tree to build up more complex
    query structures.
    """

    def __init__(self, **query):
        self.query = query

    def __repr__(self):
        return "Query(**%s)" % repr(self.query)

    def __bool__(self):
        return bool(self.query)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.query == other.query

    def accept(self, visit: 'QueryNodeVisitor') -> Union['Query', dict]:
        return visit.visit_query(self)

    @property
    def empty(self) -> bool:
        return not bool(self.query)
