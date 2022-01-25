import asyncio
import concurrent.futures
import functools
import inspect
import os
import pathlib
import tempfile
import traceback
import typing
import uuid

import fastapi
from starlette import status
from mmf_meta.descriptors import DescriptorBase
from mmf_meta.core import Target
from .fastapi_tasks import make_tasks
from .patch_upload_file import patch_upload_file

patch_upload_file()

tasks_results = pathlib.Path.cwd() / "data_results"
os.makedirs(tasks_results, exist_ok=True)


def _run_foo(t: Target, sig: inspect.Signature, args: dict, result_file: str = None):
    foo = t.foo
    for n in args:
        desc: DescriptorBase = sig.parameters[n].default
        if desc._is_file:
            args[n] = desc.load_file(args[n])
    ret = foo(**args)
    if t.returns is not None and t.returns._is_file and ret is not None:
        t.returns.to_file(ret, target_file=result_file)
        return result_file
    else:
        return ret


def _get_fastapi_spec(d: DescriptorBase):
    a, d = d.fastapi_descriptor
    return {"annotation": a, "default": d}


def wrap_fastapi(
    t: Target, pool, app: fastapi.FastAPI, task_results: dict, cancel_tasks: dict
):
    """
    Оборачиваем таргет как fastapi-совместимую функцию

    :param t:
    :param pool:
    :param app:
    :param task_results: Mapping для хранения результатов исполнения, результат - Future в текущем исполнении
    :param cancel_tasks: Список Future для отмены исполнения задачи.
    :return:
    """
    orig_sig = inspect.signature(t.foo)
    sig = orig_sig.replace(
        parameters=[
            p.replace(**_get_fastapi_spec(p.default))
            for p in orig_sig.parameters.values()
        ]
        + [
            inspect.Parameter(
                name="_back",
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation=fastapi.BackgroundTasks,
            ),
            inspect.Parameter(
                name="as_task",
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation=typing.Optional[bool],
                default=fastapi.Query(
                    False,
                    description="Если true, то задача будет поставлена в очередь, в таком случае в обязательном порядке "
                    "нужно указать заголовок TASK-ID. Запросить статус по выполнению задачи можно с помощью GET /task "
                    "Если TASK-ID пересекается с одной из задач в очереди, эта задача"
                    " отменяется, вместо нее встает новая",
                ),
            ),
            inspect.Parameter(
                name="task_id",
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation=typing.Optional[str],
                default=fastapi.Header(None, description="ID задачи для as_task=True"),
            ),
        ]
    )

    async def run_task(foo, task_id: str):
        loop = asyncio.get_event_loop()

        task: asyncio.Future = loop.run_in_executor(pool, foo)
        cancel: asyncio.Future = cancel_tasks.get(task_id)
        res: asyncio.Future = task_results.get(task_id, None)

        def on_done(_res: asyncio.Future):
            if res.done():
                return
            try:
                ret = _res.result()
                if (
                    t.returns is not None
                    and t.returns._is_file
                    and isinstance(ret, os.PathLike)
                ):
                    ret = fastapi.responses.FileResponse(
                        path=ret,
                    )
                else:
                    ret = {"result": ret}
                    ret = fastapi.responses.ORJSONResponse(content=ret)
                res.set_result(ret)
            except Exception as exc:
                res.set_exception(exc)

        task.add_done_callback(on_done)
        try:
            await asyncio.wait([task, cancel], return_when=asyncio.FIRST_COMPLETED)
            if cancel.done():
                task.cancel()
                if not task.done():
                    res.set_exception(asyncio.CancelledError())
        finally:
            cancel_tasks.pop(task_id, None)

    async def wrapper(**data):
        back: fastapi.BackgroundTasks = data.pop("_back", None)
        as_task: bool = data.pop("as_task", False)
        task_id: str = data.pop("task_id", None)
        for n, v in data.items():
            desc: DescriptorBase = orig_sig.parameters[n].default
            if desc._is_file:
                data[n] = v.get_file_name()
        if as_task and not task_id:
            raise fastapi.HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="must provide TASK-ID header if use as_task=True",
            )
        loop = asyncio.get_event_loop()
        is_file = t.returns and t.returns._is_file

        if is_file:
            result_file = (
                tasks_results
                / f"task.{task_id if task_id else uuid.uuid4().hex}.{t.returns.out_format}"
            )
        else:
            result_file = None
        foo = functools.partial(
            _run_foo,
            t,
            orig_sig,
            data,
            result_file,
        )
        if not as_task:
            try:
                ret = await loop.run_in_executor(pool, foo)
            except Exception as exc:
                raise
                raise fastapi.HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "err": True,
                        "msg": str(exc),
                        "trace": traceback.format_exc(),
                    },
                )
            if t.returns and t.returns._is_file and isinstance(ret, os.PathLike):
                return fastapi.responses.FileResponse(ret)
            else:
                return fastapi.responses.ORJSONResponse({"result": ret})
        else:
            cancel: asyncio.Future = cancel_tasks.pop(task_id, None)
            result: asyncio.Future = task_results.pop(task_id, None)
            if cancel:
                cancel.set_result(True)
            if result:
                result.set_exception(asyncio.CancelledError())

            cancel_tasks[task_id] = loop.create_future()
            task_results[task_id] = loop.create_future()
            back.add_task(functools.partial(run_task, foo, task_id))
            return fastapi.Response(status_code=200)
        # TODO: тут еще нужно поработать над get_files

    wrapper.__signature__ = sig
    wrapper.__name__ = t.foo.__name__
    wrapper = app.post(
        f"/{t.foo.__name__}",
        description=t.description,
        response_description=t.returns.description if t.returns else None,
        name=t.name,
        tags=["targets"],
    )(wrapper)
    return wrapper


def get_fastapi_app(targets: typing.List[Target], n_proc=1):
    app = fastapi.FastAPI()
    pool = concurrent.futures.ProcessPoolExecutor(n_proc)
    task_results = {}
    cancel_tasks = {}
    for t in targets:
        wrap_fastapi(t, pool, app, task_results=task_results, cancel_tasks=cancel_tasks)

    @app.get("/health", tags=["sys"])
    async def health():
        return fastapi.Response(status_code=200)

    make_tasks(app, task_results=task_results, cancel_tasks=cancel_tasks)
    return app
