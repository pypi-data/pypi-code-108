def sig_get(hub, **kwargs):
    """
    Validate the signature of the reconcile.wait get function
    """
    ...


def post_get(hub, ctx):
    """
    Conform the return value of every reconcile.wait get()
    """
    assert isinstance(ctx.ret, int)
    return ctx.ret
