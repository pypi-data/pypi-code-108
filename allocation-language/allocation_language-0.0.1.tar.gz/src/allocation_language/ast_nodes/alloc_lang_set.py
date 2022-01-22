from allocation_language.alloc_lang_data_containers.event_dataclasses import EventData
from allocation_language.ast_nodes.alloc_lang_primitives import Field, LiveVar, Node, Number, String
from typing import List


class SetValue(Node):
    def __init__(self, field_node: Field, value_node: LiveVar | Number | String):
        self.field_node = field_node
        self.value_node = value_node

    def get_live_nodes(self, found: List[str] | None = None) -> List[str]:
        if found is None:
            found = []
        if isinstance(self.value_node, LiveVar):
            found += [self.value_node.name]
        return super().get_live_nodes(found)

    def _get_node_value(self) -> float | str:
        if isinstance(self.value_node, LiveVar | Number):
            return self.value_node.num_value
        return self.value_node.string_value

    def evaluate(self, event: EventData) -> EventData:
        if not isinstance(event, EventData):
            return event
        if not event.scope_flag:
            return event

        data = event.data
        data[self.field_node.name] = self._get_node_value()
        return EventData(data=data, scope_flag=True, aggregated=event.aggregated)
