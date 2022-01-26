import json
import logging
import traceback
from dataclasses import asdict
from typing import Any, Callable

from arrlio import __tasks__
from arrlio.models import Event, Graph, Task, TaskData, TaskInstance, TaskResult
from arrlio.serializer import base
from arrlio.utils import ExtendedJSONEncoder


logger = logging.getLogger("arrlio")


class Json(base.Serializer):
    def __init__(self, encoder=None):
        self.encoder = encoder or ExtendedJSONEncoder

    def dumps_task_instance(self, task_instance: TaskInstance, **kwds) -> bytes:
        def fn(task_instance: dict):
            if graph := task_instance["data"]["graph"]:
                task_instance["data"]["graph"] = graph.dict()
            return {"name": task_instance["task"]["name"], **task_instance["data"]}

        data = fn(asdict(task_instance))
        return json.dumps(data, cls=self.encoder).encode()

    def loads_task_instance(self, data: bytes) -> TaskInstance:
        data = json.loads(data)

        def fn(data: dict, graph=None):
            if data["graph"]:
                data["graph"] = Graph.from_dict(data["graph"])
            name = data.pop("name")
            if name in __tasks__:
                task_instance = __tasks__[name].instantiate(data=TaskData(**data))
            else:
                task_instance = Task(None, name).instantiate(data=TaskData(**data))
            return task_instance

        return fn(data)

    def dumps_task_result(self, task_result: TaskResult, **kwds) -> bytes:
        if task_result.exc:
            data = (
                None,
                (
                    getattr(task_result.exc, "__module__", "builtins"),
                    task_result.exc.__class__.__name__,
                    str(task_result.exc),
                ),
                "".join(traceback.format_tb(task_result.trb, 3)) if task_result.trb else None,
            )
        else:
            data = (task_result.res, None, None)
        return json.dumps(data, cls=self.encoder).encode()

    def loads_task_result(self, data: bytes) -> TaskResult:
        return TaskResult(*json.loads(data))

    def dumps_event(self, event: Event, **kwds) -> bytes:
        data = asdict(event)
        return json.dumps(data, cls=self.encoder).encode()

    def loads_event(self, data: bytes) -> Event:
        return Event(**json.loads(data))

    def dumps(self, data: Any, **kwds) -> bytes:
        return json.dumps(data, cls=self.encoder).encode()

    def loads(self, data: bytes) -> Any:
        return json.loads(data)


class CryptoJson(Json):
    def __init__(self, encoder=None, encryptor: Callable = lambda x: x, decryptor: Callable = lambda x: x):
        super().__init__(encoder=encoder)
        self.encryptor = encryptor
        self.decryptor = decryptor

    def dumps_task_instance(self, task_instance: TaskInstance, **kwds) -> bytes:
        data: bytes = super().dumps_task_instance(task_instance, **kwds)
        if task_instance.data.encrypt:
            data: bytes = b"1" + self.encryptor(data)
        else:
            data: bytes = b"0" + data
        return data

    def loads_task_instance(self, data: bytes) -> TaskInstance:
        header, data = data[0:1], data[1:]
        if header == b"1":
            data: bytes = self.decryptor(data)
        return super().loads_task_instance(data)

    def dumps_task_result(self, task_result: TaskResult, encrypt: bool = None, **kwds) -> bytes:
        data: bytes = super().dumps_task_result(task_result, **kwds)
        if encrypt:
            data: bytes = b"1" + self.encryptor(data)
        else:
            data: bytes = b"0" + data
        return data

    def loads_task_result(self, data: bytes) -> TaskResult:
        header, data = data[0:1], data[1:]
        if header == b"1":
            data: bytes = self.decryptor(data)
        return super().loads_task_result(data)

    def dumps(self, data: Any, encrypt: bool = None, **kwds) -> bytes:
        data: bytes = super().dumps(data, **kwds)
        if encrypt:
            data: bytes = b"1" + self.encryptor(data)
        else:
            data: bytes = b"0" + data
        return data

    def loads(self, data: bytes) -> Any:
        header, data = data[0:1], data[1:]
        if header == b"1":
            data: bytes = self.decryptor(data)
        return super().loads(data)
