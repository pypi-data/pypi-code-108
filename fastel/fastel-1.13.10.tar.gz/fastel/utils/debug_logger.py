from fastapi import Request


async def debug_logger(request: Request) -> None:
    """
    Log the HTTP request to the console.

    According to this discussion: https://github.com/tiangolo/fastapi/issues/394,
    consuming request data in middleware is problematic, so we shouldn't put this kind of
    logger into the middleware.

    Instead, put in the route's dependency list like this:
    `app.include_router(api_router, dependencies=[Depends(log_json)])`
    """
    msg = ["\n*************"]
    msg += ("[URL]", str(request.url))
    try:
        data = await request.json()
        if data:
            msg += ("[JSON]", str(data))
    except Exception:
        pass
    msg += ("*************\n",)
    print("\n".join(msg))
