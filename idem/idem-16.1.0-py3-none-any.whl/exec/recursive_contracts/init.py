import asyncio
from typing import Awaitable

from idem.exec.init import ExecReturn


def _create_exec_return(ret, ref: str):
    if isinstance(ret, ExecReturn):
        return ret
    try:
        return ExecReturn(
            **ret,
            ref=ref,
        )
    except TypeError:
        raise TypeError(
            f"Exec module '{ref}' did not return a dictionary: "
            "\n{'result': True|False, 'comment': Any, 'ret': Any}"
        )


async def _create_exec_return_coro(hub, ret: Awaitable, ref: str):
    ret = await hub.pop.loop.unwrap(ret)
    return _create_exec_return(ret, ref)


def post(hub, ctx):
    """
    Convert the dict return to an immutable namespace addressable format
    """
    ref = ctx.func.__module__
    if asyncio.iscoroutine(ctx.ret):
        return _create_exec_return_coro(hub, ctx.ret, ref)
    else:
        return _create_exec_return(ctx.ret, ref)
