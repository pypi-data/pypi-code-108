from typing import List


async def sig_loop(
    hub,
    pending_plugin,
    name,
    sls_sources,
    render,
    runtime,
    cache_dir,
    sls,
    test,
    acct_file: str = None,
    acct_key: str = None,
    acct_profile: str = None,
    acct_blob: str = None,
    subs: List[str] = None,
):
    """
    Validate the signature of the reconciliation loop function
    """
    ...


def post_loop(hub, ctx):
    """
    Conform the return structure of every loop function to this format.
    """
    assert isinstance(ctx.ret["re_runs_count"], int)
    assert isinstance(ctx.ret["require_re_run"], bool)
    return ctx.ret
