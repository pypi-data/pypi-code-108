from typing import Iterable
from allocation_language.alloc_lang_data_containers.event_dataclasses import AssessmentEvent, EventData
from allocation_language.ast_nodes.alloc_lang_primitives import AggField, Field, Node

class KeylessAggregateNode(Node):
    def __init__(self, agg_field_nodes: Iterable[AggField]):
        self.agg_field_nodes = agg_field_nodes

    def evaluate_stream(self, events: Iterable[EventData]) -> Iterable[EventData]:
        events = list(events)
        temp_events = []
        for event in events:
            if not isinstance(event, EventData):
                yield event
            else:
                temp_events.append(event)

        events = temp_events
        agg_data = {}
        for agg_node in self.agg_field_nodes:
            agg_data[agg_node.name] = agg_node.evaluate_stream(events)

        yield EventData(data=agg_data, scope_flag=True, aggregated=True)

        yield from [event for event in events if not event.scope_flag]

    def evaluate(self, event: EventData) -> AssessmentEvent:
        if not event.scope_flag:
            return event
        return AssessmentEvent(event.data[self.agg_field_node.name])


class KeyedAggregateNode(Node):
    def __init__(self, key: Field, agg_field_nodes: Iterable[AggField]):
        self.key = key
        self.agg_field_nodes = agg_field_nodes

    def evaluate_stream(self, events: Iterable[EventData]) -> Iterable[EventData]:
        events = list(events)
        temp_events = []
        for event in events:
            if not isinstance(event, EventData):
                yield event
            else:
                temp_events.append(event)

        events = temp_events
        for current_key in set(
            self.key.evaluate_stream(event for event in events if event.scope_flag)
        ):
            agg_data = {}
            for agg_node in self.agg_field_nodes:
                agg_data[agg_node.name] = agg_node.evaluate_stream(
                    event for event in events if event.data[self.key.name] == current_key
                )
            agg_data[self.key.name] = current_key
            yield EventData(data=agg_data, scope_flag=True, aggregated=True)
            
        yield from [event for event in events if not event.scope_flag]

    def evaluate(self, event: EventData) -> AssessmentEvent:
        if not event.scope_flag:
            return event
        return AssessmentEvent(event.data[self.agg_field_node.name])
