from typing import List


async def loop(
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
    # This is the default reconciler
    # Reconciliation loop is skipped for backward compatibility
    return {
        "re_runs_count": 0,
        "require_re_run": False,
    }
