import asyncio
import traceback
import typing
import fastapi.routing
from starlette import status


def make_tasks(app: fastapi.FastAPI, task_results: dict, cancel_tasks: dict):
    @app.get("/task", tags=["tasks"])
    async def get_task(
        task_id: str = fastapi.Header(..., description="ID задачи"),
        auto_remove: bool = fastapi.Query(
            True, description="автоматически удалить задачу"
        ),
    ):
        """
        Возвращает результат выполнения задачи по завершению выполнения

        :param task_id:
        :return:
        """
        ret = task_results.get(task_id)
        try:
            ret = await ret
            if auto_remove:
                task_results.pop(task_id, None)
                cancel_tasks.pop(task_id, None)
            return ret
        except Exception as exc:
            raise fastapi.HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"err": True, "msg": str(exc), "trace": traceback.format_exc()},
            )

    @app.delete("/task", tags=["tasks"])
    async def delete_task(task_id: str = fastapi.Header(..., description="ID задачи")):
        """
        Удаляет/отменяет задачу

        :param task_id:
        :return:
        """
        ret: asyncio.Future = task_results.pop(task_id, None)
        if ret is None:
            return
        cancel: asyncio.Future = cancel_tasks.get(task_id, None)
        if ret.done():
            return
        elif cancel:
            cancel.set_result(True)
            ret.set_exception(asyncio.CancelledError())
            return

    @app.get("/tasks", tags=["tasks"])
    async def get_tasks(
        task_id: typing.Optional[str] = fastapi.Header(
            None,
            description="ID задачи, в данном случае не обязательный "
            "параметр, используется только, если нужно "
            "привязать запрос к определенной реплике",
        )
    ):
        """
        Список всех задач с их статусами
        :return:
        """
        done = []
        pending = []
        for task_id, task in task_results.items():
            if task.done():
                done.append(task_id)
            else:
                pending.append(task_id)
        return fastapi.responses.ORJSONResponse({"done": done, "pending": pending})

    @app.delete("/tasks", tags=["tasks"])
    async def get_tasks(
        task_id: typing.Optional[str] = fastapi.Header(
            None,
            description="ID задачи, в данном случае не обязательный "
            "параметр, используется только, если нужно "
            "привязать запрос к определенной реплике",
        ),
        only_done: bool = fastapi.Query(
            True, description="Удаляются только завершенные задачи"
        ),
    ):
        """
        Удаляются все задачи
        :return:
        """
        done = []
        pending = []
        for task_id, task in task_results.items():
            if task.done():
                done.append(task_id)
            else:
                pending.append(task_id)
        for task_id in done:
            task_results.pop(task_id, None)
            cancel_tasks.pop(task_id, None)
        if not only_done:
            for task_id in pending:
                task: asyncio.Future = task_results.pop(task_id, None)
                task.set_exception(asyncio.CancelledError())
                cancel_tasks.pop(task_id, None)
        return fastapi.responses.Response(status_code=200)
