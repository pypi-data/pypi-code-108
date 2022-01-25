import asyncio


# Implementing this contract will catch any exception from any state


def _format_error(ctx, e):
    return {
        "changes": {},
        "comment": f"{e.__class__.__name__}: {e}",
        "name": ctx.kwargs["name"],
        "result": False,
    }


async def _catch_all(hub, ctx, ret):
    try:
        return await hub.pop.loop.unwrap(ret)
    except Exception as e:
        return _format_error(ctx, e)


def call(hub, ctx):
    try:
        ret = ctx.func(*ctx.args, **ctx.kwargs)
        if asyncio.iscoroutine(ret):
            return _catch_all(hub, ctx, ret)
        else:
            return ret
    except Exception as e:
        return _format_error(ctx, e)
