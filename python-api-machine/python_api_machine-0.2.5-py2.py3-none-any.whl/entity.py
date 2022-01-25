from dataclasses import dataclass, field, fields, make_dataclass, replace
from collections import namedtuple

from .schema import dataclass_to_model
from .lifecycle import StateMachine
from .pubsub import RefStr


@dataclass
class InputMessage:
    ref: RefStr
    payload: object


@dataclass
class Message:
    ref: RefStr
    payload: object


class EntitySchema:
    pass


@dataclass
class Entity:
    name: str
    schema: object
    lifecycle: StateMachine
    mutable: set
    private: set

    key: list = field(default_factory=lambda: {'id'})
    indices: list = None

    def __post_init__(self):
        if isinstance(self.lifecycle, list):
            self.lifecycle = StateMachine(self.lifecycle)

    def create(self, values: dict):
        return self.schema(**values)

    def update(self, obj, values: dict):
        return replace(obj, **values)

    def delete(self, obj):
        return obj

    def set_status(self, obj, action):
        if hasattr(obj, "status"):
            obj.status = self.lifecycle.do(
                obj.status, action
            ).target

    def scope_transition(self, state, action, fields):
        transition = self.lifecycle[state, action]
        transition.metadata['scoped'] = {
            'fields': fields
        }

    def fields(self, include=None, aslist=False):
        result = fields(self.schema)
        if include:
            result = [f for f in result if f.name in include]
        if aslist:
            return list(
                (f.name, f.type, field(default_factory=f.default_factory))
                for f in result
            )
        return set(
            f.name for f in result
        )
