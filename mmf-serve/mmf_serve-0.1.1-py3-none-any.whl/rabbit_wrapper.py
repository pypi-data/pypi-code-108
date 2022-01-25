import asyncio
import concurrent.futures
import inspect
import logging
import traceback
import typing
from http.client import HTTPResponse
from urllib import request

import orjson
import requests
from aio_pika import connect_robust, RobustChannel, Exchange, IncomingMessage, Message

from mmf_meta.core import Target
from mmf_meta.descriptors import DescriptorBase, JsonFile, Dict

lg = logging.getLogger()


def _get_files(data, sig: inspect.Signature):
    args = {}
    for n, v in data.items():
        desc = sig.parameters.get(n)
        if desc is None:
            continue
        elif isinstance(desc.default, DescriptorBase) and desc.default.is_file:
            args[n] = desc.default.load_url(data[n])
        else:
            args[n] = v
    return args


def wrap_rabbit_s3(t: Target, msg: bytes, content_type: str):
    """
    Оборачиваем таргет как функцию, готовую принимать сообщения от rabbitmq
    Все файлы в таком случае будут ожидаться как ссылки на сетевое хранилище.
    Для s3 необходимо передавать presigned url
    Если функция возвращает файл, необходимо так же передать поле _ret_url, содержащее
    presigned url для загрузки итоговых данных.

    :param t:
    :return:
    """
    sig = inspect.signature(t.foo)

    if content_type == "json":
        data = orjson.loads(msg)
    else:
        raise TypeError(f"not compatible content_type {content_type}")
    if t.returns and t.returns.is_file and "_ret_url" not in data:
        raise ValueError(
            f"{t.name} returns file, ret_url must be provided in order to upload results"
        )
    args = _get_files(data, sig)
    ret = t.foo(**args)
    if t.returns:
        if t.returns.is_file:
            if isinstance(t.returns, JsonFile):
                if not t.returns.to_s3:
                    return orjson.dumps(ret)
            url: dict = data["_ret_url"]
            key: str = url["fields"]["key"]
            *_, ext = key.lower().split(".")
            ret = t.returns.to_file(ret, ext=ext)
            ret.seek(0)
            files = {"file": (url["fields"]["key"], ret)}
            resp = requests.post(url["url"], data=url["fields"], files=files)
            lg.debug("sending result to %s", url)

            if resp.status_code != 204:
                raise RuntimeError(
                    f"could not upload result to {url}, status: {resp.status_code}, info: {resp.content}"
                )
            return b"ok"
        elif isinstance(t.returns, Dict) and content_type == "json":
            if not isinstance(ret, dict):
                raise TypeError(
                    f"return value is expected to be dict-like, but is {type(ret)} instead"
                )
            return orjson.dumps(ret)
        else:
            return b"ok"

    return


async def serve_rabbitmq(
    n_proc: int,
    queue_name: str,
    targets: typing.List[Target],
    rabbit_params: dict,
    results_exchange: str,
):
    user = rabbit_params["user"]
    password = rabbit_params["password"]
    host = rabbit_params["host"]
    lg.info("connecting %s@%s", user, host)
    connection = await connect_robust(f"amqp://{user}:{password}@{host}/")
    channel: RobustChannel = await connection.channel()
    exchange: Exchange = await channel.get_exchange(results_exchange)
    lg.info("connecting %s", results_exchange)
    await channel.set_qos(prefetch_count=1)
    queue = await channel.get_queue(queue_name)
    lg.info("connecting %s", queue_name)
    targets = {t.name: t for t in targets}
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor(n_proc) as pool:
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    message: IncomingMessage
                    lg.debug(f"process message %s", message)
                    task_id: str = message.headers.get("task-id", None)
                    if task_id is None:
                        continue
                    try:
                        target = targets.get(message.headers.get("target"))
                        if target is None:
                            raise KeyError(f"target with key {target} dows not exists")
                        lg.debug("run %s", target)
                        ret = await loop.run_in_executor(
                            pool,
                            wrap_rabbit_s3,
                            target,
                            message.body,
                            message.content_type,
                        )
                    except Exception as exc:
                        lg.exception("while processing %s", message)
                        if message.content_type == "json":
                            ret = orjson.dumps(
                                {
                                    "error": True,
                                    "trace": traceback.format_exc(),
                                    "msg": str(exc),
                                }
                            )
                        else:
                            ret = f"ERROR: {exc}".encode()
                    lg.debug("sending results %s", ret)
                    await exchange.publish(
                        Message(ret, headers={"task-id": task_id}), routing_key=""
                    )
