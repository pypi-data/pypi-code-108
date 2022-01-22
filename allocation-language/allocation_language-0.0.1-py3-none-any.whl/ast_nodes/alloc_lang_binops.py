from allocation_language.alloc_lang_data_containers.event_dataclasses import EventData
from allocation_language.ast_nodes.alloc_lang_alloc import Node
from allocation_language.ast_nodes.alloc_lang_primitives import Field, LiveVar, Number
from typing import List

class BinOp(Node):
    def __init__(self, node_a: Node, node_b: Node):
        self.rhs: Field | LiveVar | Number = node_a
        self.lhs: Field | LiveVar | Number = node_b
    
    def get_live_nodes(self, found: List[str] | None = None) -> List[str]:
        if (found is None):
            found = []
        found += self.rhs.get_live_nodes()
        found += self.lhs.get_live_nodes()
        return found

    def update(self, name: str, value: float):
        self.rhs.update(name, value)
        self.lhs.update(name, value)

    def evaluate(self, event_data: EventData) -> float:
        a = self.rhs.evaluate(event_data)
        b = self.lhs.evaluate(event_data)
        return self.compute(a, b)


class Exponentiate(BinOp):
    def compute(self, a: float, b: float) -> float:
        return a ** b


class Multiply(BinOp):
    def compute(self, a: float, b: float) -> float:
        return a * b


class Divide(BinOp):
    def compute(self, a: float, b: float) -> float:
        return a / b


class Add(BinOp):
    def compute(self, a: float, b: float) -> float:
        return a + b


class Subtract(BinOp):
    def compute(self, a: float, b: float) -> float:
        return a - b
