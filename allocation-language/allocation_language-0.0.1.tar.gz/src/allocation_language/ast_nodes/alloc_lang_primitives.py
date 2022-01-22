from typing import Iterable, List
from allocation_language.alloc_lang_data_containers.event_dataclasses import AssessmentEvent, EventData
import allocation_language.custom_exceptions as custom_exceptions
from statistics import mean, median, mode
class Node(object):
    def __eq__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return type(self) is type(other) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)

    def get_live_nodes(self, found: List[str] | None = None) -> List[str]:
        if found is None:
            found = []
        return found

    def update(self, name: str, value: float):
        pass

    def evaluate_stream(self, event_data_stream: Iterable[EventData]) -> Iterable[EventData]:
        for event in event_data_stream:
            yield self.evaluate(event) 

    def evaluate(self, event_data: EventData) -> dict | float:
        return EventData


class Percent(Node):
    def __init__(self, string_value: str):
        self.num_value = float(string_value) / 100

    def evaluate(self, _: dict) -> float:
        return self.num_value


class Number(Node):
    def __init__(self, string_value: str):
        self.num_value = float(string_value)

    def evaluate(self, _: EventData) -> float:
        return self.num_value

class String(Node):
    def __init__(self, string_value: str):
        self.string_value = string_value

    def evaluate(self, _: EventData) -> str:
        return self.string_value


class Field(Node):
    def __init__(self, string_name: str):
        self.name = string_name

    def evaluate(self, event_data: EventData) -> float:
        if self.name not in event_data.data:
            raise custom_exceptions.FieldNotInDataError(event_data, self.name)
        return event_data.data[self.name]

class AggField(Field):
    def __init__(self, string_name: str, agg_mode: str):
        self.agg_mode = agg_mode
        super().__init__(string_name)
        
    def evaluate_stream(self, events: Iterable[EventData]) -> float | str:
        events = [event for event in events if not isinstance(event, AssessmentEvent)]
        values = [self.evaluate(event) for event in events]
        match self.agg_mode:
            case "sum":
                return sum(values)
            case "mean":
                return mean(values)
            case "median":
                return median(values)
            case "mode":
                return mode(values)
            case "max":
                return max(values)
            case "min":
                return min(values)
            case "count":
                return len(set(values))
            case _:
                pass

class LiveVar(Node):
    def __init__(self, string_name: str):
        self.name = string_name
        self.num_value: float = 0.0

    def get_live_nodes(self, found=None):
        if (found is None):
            found = [self.name]
        return found

    # Catch any valid updates that are sent down the tree
    def update(self, name: str, value: float):
        if self.name == name:
            self.num_value = value

    def evaluate(self, _: EventData) -> float:
        return self.num_value
