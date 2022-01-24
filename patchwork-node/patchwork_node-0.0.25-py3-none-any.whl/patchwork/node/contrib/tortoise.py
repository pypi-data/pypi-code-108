# -*- coding: utf-8 -*-
from types import ModuleType
from typing import Optional, Dict, Iterable, Union

from patchwork.node import PatchworkWorker
from patchwork.node.core.exceptions import TaskFatal

try:
    from tortoise import Tortoise, exceptions
except ImportError:
    raise RuntimeError("Tortoise-ORM seems to be not installed")


def register_tortoise(
        worker: PatchworkWorker,
        config: Optional[dict] = None,
        config_file: Optional[str] = None,
        db_url: str = None,
        modules: Optional[Dict[str, Iterable[Union[str, ModuleType]]]] = None,
        generate_schemas: bool = False,
        add_exception_handlers: bool = False,
):
    @worker.on_event("startup")
    async def init_orm() -> None:
        await Tortoise.init(config=config, config_file=config_file, db_url=db_url, modules=modules)
        if generate_schemas:
            await Tortoise.generate_schemas()

    @worker.on_event("shutdown")
    async def close_orm() -> None:
        await Tortoise.close_connections()

    if add_exception_handlers:
        @worker.exception_handler(exceptions.OperationalError)
        async def handle_tortoise_orm_exceptions(task, receiver, exc):
            # operational error are related to data, so it make no sense to retry this task
            raise TaskFatal(reason=f"Tortoise ORM Operational Error: {exc.__class__.__name__}({exc})")
