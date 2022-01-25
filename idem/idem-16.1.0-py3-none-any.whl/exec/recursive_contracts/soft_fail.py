# Implementing this contract will catch any exception from any exec module function
import asyncio


def _run_catching_errors(ctx):
    try:
        return ctx.func(*ctx.args, **ctx.kwargs)
    except Exception as e:
        return _format_error(e)


async def _arun_catching_errors(hub, ctx):
    try:
        ret = ctx.func(*ctx.args, **ctx.kwargs)
        return await hub.pop.loop.unwrap(ret)
    except Exception as e:
        return _format_error(e)


def _format_error(e: Exception):
    return dict(comment=f"{e.__class__.__name__}: {e}", result=False, ret=None)


def call(hub, ctx):
    if asyncio.iscoroutinefunction(ctx.func):
        return _arun_catching_errors(hub, ctx)
    else:
        return _run_catching_errors(ctx)
