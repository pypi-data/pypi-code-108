from dataclasses import dataclass, asdict, field
import typing

from . import exc, events
from .lifecycle import Transition
from .entity import Entity, InputMessage, Message
from .pubsub import Broadcaster, RefStr
from .schema import (
    extract_schema, dataclass_to_model, ValidationError,
    serialize
)


@dataclass
class OperationContext:
    service: object
    repository: object
    entity: Entity

    def create(self, values):
        instance = self.entity.create(values)
        return self.repository.insert(
            serialize(instance)
        )

    def get(self, key):
        return self.entity.create(
            self.repository.get(key)
        )

    def update(self, key, instance, values):
        new_instance = self.entity.update(
            instance, values
        )
        return self.repository.update(
            key, serialize(new_instance)
        )

    def list(self, payload):
        list_params = asdict(payload)
        return self.repository.list(
            list_params.pop('expr'),
            **list_params['params']
        ).serialize(self.entity.create)


@dataclass
class Operation:
    action: str
    entity: Entity
    input_model: object
    private_model: object = None
    output_model: object = None
    __action_type__ = None
    __result_type__ = None

    @property
    def ref(self):
        return ":".join([
            self.entity.name, self.__action_type__,
            self.action
        ])

    @property
    def output_ref(self):
        return ":".join([
            self.entity.name, self.__result_type__,
            self.action
        ])

    def create_context(self, service):
        repo = service.repos[self.entity.name]
        return OperationContext(
            service,
            repo, self.entity
        )

    @staticmethod
    def name(action, entity):
        return "".join(c.capitalize() for c in [
            action, entity.name
        ])

    @classmethod
    def create(cls, action, entity, scope=None):
        fields = scope or cls.get_fields(
            entity
        )
        input_fields = fields - entity.private
        name = cls.name(action, entity)
        return cls(
            action, entity,
            input_model=extract_schema(name, entity, input_fields),
            private_model=extract_schema(name, entity, fields),
            output_model=entity.schema
        )

    @classmethod
    def get_fields(cls, entity):
        return entity.fields()

    def deserialize(self, payload):
        try:
            obj = self.input_model(**payload)
        except ValidationError as e:
            raise exc.ValidationError(
                e.json()
            )

        if self.private_model:
            return self.private_model(**asdict(obj))
        return obj

    def get_primary_key(self, payload):
        return dict(
            (k, getattr(payload, k)) for k in self.entity.key
        )

    def __call__(self, context: OperationContext, msg: InputMessage):
        msg = Message(
            ref=RefStr(self.ref),
            payload=self.deserialize(msg.payload),
        )
        return self.execute(context, msg)


class Mutation(Operation):
    __action_type__ = "command"
    __result_type__ = "event"


class Query(Operation):
    __action_type__ = "query"
    __result_type__ = "result"


class CreateOperation(Mutation):
    __action_type__ = "command"

    def execute(self, context: OperationContext, msg):
        values = asdict(msg.payload)
        return context.create(values)


class GetOperation(Query):
    @classmethod
    def get_fields(cls, entity):
        return entity.key

    def execute(self, context: OperationContext, msg):
        key = self.get_primary_key(msg.payload)
        return context.get(key)


class UpdateOperation(Mutation):
    @classmethod
    def get_fields(cls, entity):
        fields = super().get_fields(entity)
        return entity.key & fields & entity.mutable

    def execute(self, context: OperationContext, msg):
        key = self.get_primary_key(msg.payload)
        instance = context.get(key)
        context.entity.set_status(instance, self.action)
        msg.payload.status = instance.status
        return context.update(key, instance, asdict(msg.payload))


class ListOperation(Query):
    @classmethod
    def create(cls, action, entity):
        class ListModel:
            expr: str = ""
            params: dict = field(default_factory=dict)

        class EntityList:
            items: typing.List[entity.schema]

        model = dataclass_to_model(ListModel)
        output_model = dataclass_to_model(EntityList)

        return cls(
            action, entity,
            input_model=model, private_model=model,
            output_model=output_model
        )

    def execute(self, context: OperationContext, msg):
        return context.list(msg.payload)


def action_to_operation(from_state: str, action: str):
    if from_state is None:
        return CreateOperation
    return {
        'create': CreateOperation,
        'update': UpdateOperation,
    }.get(action, UpdateOperation)


class OperationRegistry(dict):
    def append(self, operation: Operation):
        self[operation.ref] = operation


class Service:
    operations = None
    entities = None

    def __init__(self, name):
        self.operations = OperationRegistry()
        self.entities = {}
        self.name = name
        self.events = Broadcaster()
        self.repos = {}

    def mount_entity(self, entity, repository):
        for transition in entity.lifecycle.transitions:
            params = transition.metadata or {}

            scope = None
            try:
                scope = params['scoped']['fields']
            except KeyError:
                pass

            operation_cls = action_to_operation(
                transition.state, transition.action
            )
            operation = operation_cls.create(
                transition.action, entity,
                scope=scope
            )
            self.mount_operation(operation)

        self.mount_operation(
            GetOperation.create("get", entity)
        )
        self.mount_operation(
            ListOperation.create("list", entity)
        )
        self.repos[entity.name] = repository
        self.entities[entity.name] = entity

    def mount_operation(self, operation: Operation):
        self.operations.append(operation)

    def get_key(self, entity_name: str):
        return self.entities[entity_name].key

    def __call__(self, msg: InputMessage):
        scoped_ref = ":".join(msg.ref.split(":")[1:])
        try:
            operation = self.operations[scoped_ref]
        except KeyError:
            raise exc.OperationDoesNotExist()

        context = operation.create_context(
            self
        )
        self.events.accept(
            events.ServiceBeforeCall,
            events.ServiceBeforeCall(
                msg=msg
            )
        )
        try:
            result = operation(
                context,
                msg
            )
            event = events.ServiceAfterSuccess

        except exc.ClientError as e:
            result = Message(
                RefStr("{self.name}:system:result:error"),
                e.payload
            )
            event = events.ServiceAfterFail
        else:
            result = Message(
                RefStr(f"{self.name}:{operation.output_ref}"),
                result
            )

        self.events.accept(
            event,
            event(
                msg=msg, result=result
            )
        )

        return result

    def get(self, entity, key):
        return self(InputMessage(
            f"{self.name}:{entity}:query:get",
            key
        ))

    def list(self, entity, payload):
        return self(InputMessage(
            f"{self.name}:{entity}:query:list",
            payload
        ))

    def action(self, entity, action, payload: dict):
        return self(InputMessage(
            f"{self.name}:{entity}:command:{action}",
            payload
        ))
