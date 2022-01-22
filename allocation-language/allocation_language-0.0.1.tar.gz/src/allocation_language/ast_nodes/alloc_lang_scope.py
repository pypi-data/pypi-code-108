from allocation_language.alloc_lang_data_containers.event_dataclasses import EventData
from allocation_language.ast_nodes.alloc_lang_primitives import Node

# Only used for typing purposes really
class BoolNode(Node):
    def evaluate(self, _: EventData) -> bool:
        return True

class Condition(BoolNode):
    def __init__(self, rhs: Node, comparator: str, lhs: Node):
        self.rhs = rhs
        self.lhs = lhs

        self.comparator = comparator

    def evaluate(self, event: EventData) -> bool:
        rh_val: float | str = self.rhs.evaluate(event)
        lh_val: float | str = self.lhs.evaluate(event)

        return bool(eval(f"{rh_val!r} {self.comparator} {lh_val!r}"))

class AndNode(BoolNode):
    def __init__(self, rhs: BoolNode, lhs: BoolNode):
        self.rhs = rhs
        self.lhs = lhs

    def evaluate(self, event: EventData) -> bool:
        return self.rhs.evaluate(event) and self.lhs.evaluate(event)


class OrNode(BoolNode):
    def __init__(
        self, rhs: BoolNode, lhs: BoolNode
    ):
        self.rhs = rhs
        self.lhs = lhs

    def evaluate(self, event: EventData) -> bool:
        return self.rhs.evaluate(event) or self.lhs.evaluate(event)


class Scope(Node):
    def __init__(self, condition: BoolNode):
        self.condition = condition

    def evaluate(self, event: EventData) -> EventData:
        if (not isinstance(event, EventData)):
            return event
        return EventData(data=event.data, scope_flag=self.condition.evaluate(event))
