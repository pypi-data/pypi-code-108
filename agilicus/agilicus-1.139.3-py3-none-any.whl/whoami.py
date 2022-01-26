from . import context


def whoami(ctx, refresh, **kwargs):
    return context.get_token(ctx, refresh=refresh)


def whoami_id(ctx, refresh, **kwargs):
    return context.get_id_token(ctx, refresh=refresh)
