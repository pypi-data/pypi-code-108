def sig_is_pending(hub, ret):
    """
    Validate the signature of the pending plugin function
    """
    ...


def post_is_pending(hub, ctx):
    """
    Conform the return structure of is_pending is a boolean
    """
    assert isinstance(ctx.ret, bool), ctx.ret
    return ctx.ret
